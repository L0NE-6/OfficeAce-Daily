import sys
import unittest
from pathlib import Path
from unittest import mock


sys.path.insert(0, str(Path(__file__).resolve().parent))

from _loader import load_script


OA = load_script("officeace_daily_readback", "officeace_daily.py")
ACCOUNT = {
    "note": "fixture",
    "ak": "fixture-ak",
    "sk": "fixture-sk",
    "sts": "fixture-sts",
    "project": "fixture-project",
    "base": "https://example.invalid",
}


def subscription(*bonuses):
    return {
        "bonus_skus": [
            {
                "activity_id": key,
                "activity_name": key,
                "points": str(points),
                "current_value": str(current),
            }
            for key, points, current in bonuses
        ]
    }


class OfficeAceReadbackTests(unittest.TestCase):
    def run_checkin(
        self,
        before=None,
        after=None,
        claim=None,
        before_error=None,
        after_error=None,
    ):
        fetch_results = [
            before_error if before_error is not None else before,
            after_error if after_error is not None else after,
        ]
        with mock.patch.object(
            OA, "fetch_subscription", side_effect=fetch_results
        ) as fetch, mock.patch.object(
            OA, "claim_bonus", return_value=claim or {}
        ) as claim_call, mock.patch.object(OA, "log"):
            result = OA.checkin(ACCOUNT)
        return result, fetch, claim_call

    def test_positive_before_after_delta_is_confirmed(self):
        (ok, message), fetch, claim = self.run_checkin(
            before=subscription(("daily", 100, 0)),
            after=subscription(("daily", 100, 50)),
            claim={"bonus_skus": [{"activity_id": "daily", "current_value": "50"}]},
        )

        self.assertTrue(ok)
        self.assertIn("+50", message)
        self.assertEqual(2, fetch.call_count)
        claim.assert_called_once()

    def test_empty_claim_receipt_is_explicit_no_reward(self):
        state = subscription(("daily", 100, 50))
        (ok, message), _, _ = self.run_checkin(
            before=state,
            after=state,
            claim={"bonus_skus": []},
        )

        self.assertTrue(ok)
        self.assertIn("今日无可领", message)

    def test_claim_entries_without_subscription_increment_are_not_success(self):
        state = subscription(("daily", 100, 50))
        (ok, message), _, _ = self.run_checkin(
            before=state,
            after=state,
            claim={"bonus_skus": [{"activity_id": "daily", "current_value": "50"}]},
        )

        self.assertFalse(ok)
        self.assertIn("未确认新增", message)

    def test_before_read_failure_is_unconfirmed_even_when_claim_succeeds(self):
        (ok, message), fetch, claim = self.run_checkin(
            before_error=RuntimeError("fixture before read failed"),
            after=subscription(("daily", 100, 50)),
            claim={"bonus_skus": [{"activity_id": "daily", "current_value": "50"}]},
        )

        self.assertFalse(ok)
        self.assertIn("结果未确认", message)
        self.assertIn("签到前", message)
        self.assertEqual(2, fetch.call_count)
        claim.assert_called_once()

    def test_after_read_failure_is_unconfirmed(self):
        (ok, message), _, claim = self.run_checkin(
            before=subscription(("daily", 100, 0)),
            after_error=RuntimeError("fixture after read failed"),
            claim={"bonus_skus": [{"activity_id": "daily", "current_value": "50"}]},
        )

        self.assertFalse(ok)
        self.assertIn("结果未确认", message)
        self.assertIn("签到后", message)
        claim.assert_called_once()

    def test_malformed_subscription_shape_is_unconfirmed(self):
        (ok, message), _, _ = self.run_checkin(
            before=subscription(("daily", 100, 0)),
            after={},
            claim={"bonus_skus": []},
        )

        self.assertFalse(ok)
        self.assertIn("结果未确认", message)
        self.assertIn("bonus_skus", message)

    def test_new_activity_counts_as_confirmed_increment(self):
        (ok, message), _, _ = self.run_checkin(
            before=subscription(("daily", 100, 0)),
            after=subscription(("daily", 100, 0), ("new-user", 200, 100)),
            claim={"bonus_skus": [{"activity_id": "new-user", "current_value": "100"}]},
        )

        self.assertTrue(ok)
        self.assertIn("+100", message)


if __name__ == "__main__":
    unittest.main()
