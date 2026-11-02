# 🏢 OfficeAce Daily

**Daily reward collection for OfficeAce / OfficeClaw, with built-in V11-HMAC-SHA256 signing and subscription read-back.**

[简体中文](../README.md) | [English](README.en.md) | [繁體中文](README.zh-Hant.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português (BR)](README.pt-BR.md)

> Complete Chinese documentation: [../README.md](../README.md)

## Overview

OfficeAce Daily claims the rewards currently available for an OfficeAce / OfficeClaw account. Daily check-in and the one-time new-user benefit are delivered by the same server-side claim action. The script reads the subscription before the claim and reports the actual quota increase when the service returns enough data. Repeated claims are handled as an idempotent "nothing available today" or "already claimed" result.

Control-plane requests use temporary Huawei Cloud AK/SK credentials, a security token, and a project ID. The documented lifetime is about two hours. A gateway Basic credential can remain valid much longer, but it is used for model forwarding and is not sufficient by itself for check-in.

## Core capabilities

- Claims the current daily and new-user rewards in one request.
- Implements V11-HMAC-SHA256 for the `cn-southwest-2/apic` scope.
- Reads the subscription before the claim and compares `current_value` in the claim response when available.
- Supports multiple accounts with `OFFICEACE_TOKENS`.
- Provides `--query` for a read-only quota check.
- Runs as a single self-contained Python script.
- Supports optional WeCom and PushPlus notifications.

## Credential limits

| Credential | Lifetime | Purpose | Read by `officeace_get_token.py` |
| :--- | :--- | :--- | :--- |
| Gateway Basic `key:secret` | does not expire | Model forwarding | Yes |
| Control-plane AK/SK + STS + `project_id` | about 2 hours | Quota and check-in | No |

The desktop `models.json` can provide the gateway base URL and Basic credential. The temporary control-plane credential must be obtained through the client or console flow and injected separately.

## Reading the local desktop configuration

```bash
python officeace_get_token.py
python officeace_get_token.py --list
python officeace_get_token.py --json
python officeace_get_token.py --path <file-or-directory>
```

By default the helper searches:

```text
~/.office-claw/.jiuwenclaw/config/routing_state/users/<account-id>/models.json
```

It supports either an `api_key` containing `key:secret` or an `Authorization: Basic ...` header under `custom_headers`.

## Minimum Qinglong setup

1. Upload `officeace_daily.py` to Qinglong.
2. Add `OFFICEACE_TOKENS`.
3. Create a scheduled task with:

```bash
task officeace_daily.py
```

Suggested cron:

```cron
10 9 * * *
```

Multi-account format:

```text
remark|AK_VALUE|SK_VALUE|STS_VALUE|PROJECT_ID|https://modelgw-xxxx.cn-southwest-2.huaweicloud-agentarts.com/v2
second|AK_VALUE|SK_VALUE|STS_VALUE|PROJECT_ID|https://modelgw-yyyy.cn-southwest-2.huaweicloud-agentarts.com/v2
```

The five-field form without a remark is also accepted. Use newlines or `&` between accounts.

## Minimum GitHub Actions setup

Add these Secrets under **Settings → Secrets and variables → Actions**:

| Secret | Required | Purpose |
| :--- | :---: | :--- |
| `OFFICEACE_TOKENS` | yes | Temporary control-plane credentials |
| `QYWX_TOKEN` | optional | WeCom bot key |
| `PLUSPLUS_TOKEN` | optional | PushPlus token |

The bundled workflow is manual-only by default. Run **Actions → OfficeAce Daily → Run workflow** for validation. To enable the schedule, uncomment:

```yaml
schedule:
  - cron: '10 1 * * *'
```

The expression uses UTC. `10 1 * * *` is 09:10 Beijing time. Because the control-plane credential expires after roughly two hours, a scheduled Action needs a valid temporary credential in the Secret at run time.

## Key environment variables

| Variable | Required | Description |
| :--- | :---: | :--- |
| `OFFICEACE_TOKENS` | for multi-account | Multi-account entries, with five or six fields per line |
| `OFFICEACE_AK` | optional | Single-account Access Key |
| `OFFICEACE_SK` | optional | Single-account Secret Key |
| `OFFICEACE_STS` | optional | Single-account security token |
| `OFFICEACE_PROJECT_ID` | optional | Single-account project ID |
| `OFFICEACE_BASE_URL` | optional | Single-account gateway base URL |
| `OFFICEACE_CLIENT_DIR` | optional | Search root for the local credential reader |
| `QYWX_TOKEN` | optional | WeCom bot key; `WECHAT_WEBHOOK` is also accepted |
| `PLUSPLUS_TOKEN` | optional | PushPlus token |
| `NO_NOTIFY` | optional | Set to `1` to disable notifications |

`OFFICEACE_TOKENS` takes precedence over the single-account variables.

## Command-line options

| Option | Effect |
| :--- | :--- |
| none | Claim rewards for every account |
| `--only N` | Run account number N only |
| `--query` | Read quota and activity state without claiming |

Use `NO_NOTIFY=1` in the environment to disable notifications.

## Verification scope

The repository records six official signing vectors matched byte for byte, including SDK / V11 behavior, escaped paths, query ordering, and the V11 derived-key representation. Offline checks also cover a `+50` quota delta, idempotent claims, temporary-credential expiry, multiple accounts, masking, and GBK console safety.

No real-account online claim result is included in the repository evidence. For the first live run, use `--query` to check the credential, base URL, and subscription endpoint before enabling a claim schedule.

## Privacy

The scripts do not persist control-plane credentials. `officeace_get_token.py` only reads local configuration. Logs show masked AK fragments. Never publish `OFFICEACE_TOKENS`, STS values, a complete `models.json`, or unredacted logs in a repository, Issue, or public Actions output.

## Usage and redistribution

The official repository, scripts, deployment instructions, and releases are and remain free. Without explicit written permission, do not package this project as a paid resource, paid deployment service, or paid update service; do not remove attribution and claim the work as original; do not impersonate the author; and do not use the author's identity, name, avatar, or payment QR codes to imply official endorsement. Do not repost the project through unrelated accounts, groups, channels, or paid platforms for follower growth, traffic diversion, or resale. Violations may lead to a takedown request, and the author may pause updates or archive or delete the repository. Read the full [NOTICE.md](../NOTICE.md).

## Links

- [Releases](https://github.com/L0NE-6/OfficeAce-Daily/releases)
- [Issues](https://github.com/L0NE-6/OfficeAce-Daily/issues)
- [Chinese README](../README.md)
- [Changelog](../CHANGELOG.md)

## Disclaimer

This project is intended for personal learning and automation. Follow the terms of OfficeAce, OfficeClaw, Huawei Cloud, and related services. Use it at your own risk.
