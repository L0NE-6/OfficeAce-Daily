#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏢 OfficeAce（华为云果办 / OfficeClaw）每日签到 - 青龙脚本

每日奖励领取：把当天所有可领的奖励（每日签到 + 一次性新人礼）一次领掉。
上游 `POST /v1/subscription/bonus/claim` 幂等：一天一个活动只能领一次，
重复调不报错（返回同一份列表）。

控制面接口走 **V11-HMAC-SHA256** 签名（区域作用域 apic），凭据是华为云临时
AK/SK + security_token + project_id（实测约 2 小时有效）。

环境变量：
  OFFICEACE_TOKENS   多账号，换行或 & 分隔，每条：
                     `AK|SK|security_token|project_id|base_url`
                     或 `备注|AK|SK|security_token|project_id|base_url`
  OFFICEACE_BASE_URL 单账号兜底（配合 OFFICEACE_AK / OFFICEACE_SK 等）
  OFFICEACE_AK / OFFICEACE_SK / OFFICEACE_STS / OFFICEACE_PROJECT_ID
  OFFICEACE_RETRIES  claim 重试次数（默认 2）
  QYWX_TOKEN        企业微信机器人（也兼容 WECHAT_WEBHOOK）
  PLUSPLUS_TOKEN    PushPlus
  NO_NOTIFY         设 1 关闭推送

用法：
  python officeace_daily.py             # 全部账号
  python officeace_daily.py --only 1    # 只跑第 1 个
  python officeace_daily.py --query     # 只读查询积分，不领取

依赖：Python 3.8+，仅标准库。
"""

import base64
import hashlib
import hmac as _hmaclib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_REGION = "cn-southwest-2"
TIMEOUT = 20
ONLY = None
QUERY_ONLY = False


def log(msg):
    try:
        print("%s %s" % (time.strftime("[%H:%M:%S]"), msg), flush=True)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or "utf-8"
        print(("%s %s" % (time.strftime("[%H:%M:%S]"), msg)).encode(encoding, "replace").decode(encoding), flush=True)


def mask(text, keep=4):
    text = str(text or "")
    if len(text) <= keep + 4:
        return "*" * len(text)
    return text[:keep] + "****" + text[-4:]


def num(value):
    """上游数值字段常是字符串，统一按 JS Number() 口径读。"""
    if isinstance(value, bool):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except Exception:
            return 0.0
    return 0.0


# ────────────────────────── 签名（SDK / V11） ──────────────────────────# -*- coding: utf-8 -*-
"""OfficeAce 的 SDK-HMAC-SHA256 / V11-HMAC-SHA256 签名（Python 版）。"""
import hashlib
import hmac as _hmaclib

SDK_ALGORITHM = "SDK-HMAC-SHA256"
V11_ALGORITHM = "V11-HMAC-SHA256"
SCOPE_SERVICE = "apic"
EMPTY_BODY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
DEFAULT_REGION = "cn-southwest-2"

_UNRESERVED = set(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_.~")


def _encode_component(data):
    out = []
    for b in data:
        if b in _UNRESERVED:
            out.append(chr(b))
        else:
            out.append("%%%02X" % b)
    return "".join(out)


def _unhex(a, b):
    digits = "0123456789abcdef"
    la = digits.find(chr(a).lower())
    lb = digits.find(chr(b).lower())
    if la < 0 or lb < 0:
        return None
    return (la << 4) | lb


def _decode_component(text):
    raw = text.encode("utf-8")
    out = bytearray()
    i = 0
    n = len(raw)
    while i < n:
        if raw[i] == 0x25 and i + 2 < n:
            hi = _unhex(raw[i + 1], raw[i + 2])
            if hi is not None:
                out.append(hi)
                i += 3
                continue
        out.append(raw[i])
        i += 1
    return bytes(out)


def _decode_form(text):
    return _decode_component(text.replace("+", " ")).decode("utf-8", "replace")


def _canonical_uri(path):
    path = path or "/"
    escaped = "/".join(_encode_component(_decode_component(seg)) for seg in path.split("/"))
    return escaped if escaped.endswith("/") else escaped + "/"


def _canonical_query(raw_query):
    if not raw_query:
        return ""
    pairs = []
    for part in raw_query.split("&"):
        if not part:
            continue
        if "=" in part:
            key, value = part.split("=", 1)
        else:
            key, value = part, ""
        pairs.append((_decode_form(key), _decode_form(value)))
    pairs.sort(key=lambda kv: (kv[0], kv[1]))
    return "&".join("%s=%s" % (_encode_component(k.encode()), _encode_component(v.encode()))
                    for k, v in pairs)


def _split_path_query(url):
    if "://" not in url:
        raise ValueError("地址缺少 scheme：%s" % url)
    rest = url.split("://", 1)[1]
    rest = rest.split("#", 1)[0]
    path_query = rest[rest.index("/"):] if "/" in rest else "/"
    if "?" in path_query:
        path, query = path_query.split("?", 1)
    else:
        path, query = path_query, ""
    return path, query


def _authority_of(url):
    rest = url.split("://", 1)[1]
    cut = len(rest)
    for ch in ("/", "?", "#"):
        idx = rest.find(ch)
        if idx >= 0:
            cut = min(cut, idx)
    return rest[:cut].rsplit("@", 1)[-1]


def _sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def _hmac_raw(key, message):
    return _hmaclib.new(key, message.encode("utf-8"), hashlib.sha256).digest()


def _hmac_hex(key, message):
    return _hmaclib.new(key, message.encode("utf-8"), hashlib.sha256).hexdigest()


class Credential:
    def __init__(self, access_key_id, secret_access_key, security_token="", project_id=""):
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.security_token = security_token
        self.project_id = project_id


def sign(credential, method, url, headers=None, body=b"", algorithm=V11_ALGORITHM,
         region=DEFAULT_REGION, date_override=None):
    if not credential.access_key_id or not credential.secret_access_key:
        raise ValueError("凭据不完整：access key 与 secret key 都得有")
    path, raw_query = _split_path_query(url)

    items = []

    def set_header(name, value):
        low = name.lower()
        for idx, (existing, _) in enumerate(items):
            if existing.lower() == low:
                items[idx] = (name, value)
                return
        items.append((name, value))

    def has_header(name):
        return any(existing.lower() == name.lower() for existing, _ in items)

    for name, value in (headers or {}).items():
        set_header(name, value)
    if credential.security_token:
        set_header("X-Security-Token", credential.security_token)
    if credential.project_id:
        set_header("X-Project-ID", credential.project_id)
    if date_override:
        set_header("X-Sdk-Date", date_override)
    elif not has_header("X-Sdk-Date"):
        import time
        set_header("X-Sdk-Date", time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))
    if not has_header("Host"):
        set_header("Host", _authority_of(url))

    date = ""
    for name, value in items:
        if name.lower() == "x-sdk-date":
            date = value
            break

    canonical = sorted((name.lower(), " ".join(value.split())) for name, value in items)
    canonical_headers = "".join("%s:%s\n" % (name, value) for name, value in canonical)
    signed_headers = ";".join(name for name, _ in canonical)

    payload_hash = EMPTY_BODY_SHA256 if not body else _sha256_hex(body)
    canonical_request = "\n".join([method.upper(), _canonical_uri(path), _canonical_query(raw_query),
                                   canonical_headers, signed_headers, payload_hash])

    if algorithm == SDK_ALGORITHM:
        string_to_sign = "\n".join([SDK_ALGORITHM, date, _sha256_hex(canonical_request.encode())])
        signature = _hmac_hex(credential.secret_access_key.encode(), string_to_sign)
        authorization = ("%s Access=%s, SignedHeaders=%s, Signature=%s"
                         % (SDK_ALGORITHM, credential.access_key_id, signed_headers, signature))
    else:
        scope = "%s/%s/%s" % (date[:8], region, SCOPE_SERVICE)
        string_to_sign = "\n".join([V11_ALGORITHM, date, scope, _sha256_hex(canonical_request.encode())])
        step1 = _hmac_raw(credential.access_key_id.encode(), credential.secret_access_key)
        seed = scope.encode() + b"\x01"
        derived = _hmac_raw(step1, seed.decode("latin-1"))[:32]
        signing_key_hex = "".join("%02x" % b for b in derived)
        signature = _hmac_hex(signing_key_hex.encode(), string_to_sign)
        authorization = ("%s Credential=%s/%s, SignedHeaders=%s, Signature=%s"
                         % (V11_ALGORITHM, credential.access_key_id, scope, signed_headers, signature))

    set_header("Authorization", authorization)
    return dict(items), {"canonical_request": canonical_request, "string_to_sign": string_to_sign,
                         "signed_headers": signed_headers, "signature": signature}

# ────────────────────────── 控制面调用 ──────────────────────────
def gateway_base(base_url):
    """账号里存的 `https://{host}/v2` → 网关根。"""
    trimmed = (base_url or "").strip().rstrip("/")
    if trimmed.endswith("/v2"):
        trimmed = trimmed[:-3].rstrip("/")
    return trimmed


def call_control_plane(credential, base_url, method, path, body=None, extra_headers=None):
    """调一次 V11 签名的订阅族接口，返回解析后的 JSON。"""
    base = gateway_base(base_url)
    if not base:
        raise RuntimeError("缺少模型网关基址（base_url）")
    url = base + path
    headers = dict(extra_headers or {})
    payload = b""
    if body is not None:
        payload = json.dumps(body, separators=(",", ":")).encode("utf-8")
        headers["Content-Type"] = "application/json"
    signed, _ = sign(credential, method, url, headers, payload,
                     algorithm=V11_ALGORITHM, region=DEFAULT_REGION)
    request = urllib.request.Request(url, data=payload if payload else None, method=method)
    for name, value in signed.items():
        if name.lower() == "host":
            continue
        request.add_header(name, value)
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            text = response.read().decode("utf-8", "replace")
            status = response.status
    except urllib.error.HTTPError as error:
        status = error.code
        text = error.read().decode("utf-8", "replace")
    except Exception as error:
        raise RuntimeError("请求失败：%s" % error)
    if status in (401, 403):
        raise RuntimeError("控制面凭据已失效（临时 AK/SK 约 2 小时过期）——请重新从客户端/控制台导入一次")
    if status != 200:
        raise RuntimeError("接口返回 HTTP %s：%s" % (status, " ".join(text.split())[:200]))
    try:
        return json.loads(text)
    except Exception:
        raise RuntimeError("接口响应不是合法 JSON：%s" % " ".join(text.split())[:200])


def fetch_subscription(credential, base_url):
    return call_control_plane(credential, base_url, "GET", "/v1/subscription",
                              extra_headers={"x-subscription-type": "v2"})


def claim_bonus(credential, base_url):
    """领奖励（body 必须是 {}；裸 POST 会 500）。"""
    return call_control_plane(credential, base_url, "POST", "/v1/subscription/bonus/claim",
                              body={}, extra_headers={"x-subscription-type": "v2"})


def bonuses_of(subscription):
    items = subscription.get("bonus_skus")
    if not isinstance(items, list):
        return []
    out = []
    for item in items:
        if not isinstance(item, dict):
            continue
        key = (item.get("activity_id") or item.get("cbc_resource_id")
               or item.get("activity_name") or "").strip()
        if not key:
            continue
        out.append({
            "key": key,
            "name": (item.get("activity_name") or key).strip(),
            "total": num(item.get("points")),
            "used": num(item.get("current_value")),
        })
    return out


def claimed_sum(subscription):
    """已领累计：`current_value` 之和 —— 增量的正确口径。"""
    return sum(b["used"] for b in bonuses_of(subscription))


def quota_sum(subscription):
    """奖励额度合计（展示用）：`points` 之和。"""
    return sum(b["total"] for b in bonuses_of(subscription))


# ────────────────────────── 账号 / 推送 / 入口 ──────────────────────────
def parse_accounts(raw):
    accounts = []
    for index, line in enumerate((raw or "").replace("&", "\n").splitlines(), 1):
        line = line.strip().strip('"\'')
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        note, ak, sk, sts, project, base = "账号%d" % index, "", "", "", "", ""
        if len(parts) == 5:
            ak, sk, sts, project, base = parts
        elif len(parts) >= 6:
            note, ak, sk, sts, project, base = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
        else:
            continue
        if not (ak and sk and base):
            continue
        accounts.append({"note": note, "ak": ak, "sk": sk, "sts": sts,
                         "project": project, "base": base})
    return accounts


def load_accounts():
    raw = os.environ.get("OFFICEACE_TOKENS", "").strip()
    accounts = parse_accounts(raw)
    if accounts:
        return accounts
    ak = os.environ.get("OFFICEACE_AK", "").strip()
    sk = os.environ.get("OFFICEACE_SK", "").strip()
    base = os.environ.get("OFFICEACE_BASE_URL", "").strip()
    if ak and sk and base:
        return [{"note": "账号1", "ak": ak, "sk": sk,
                 "sts": os.environ.get("OFFICEACE_STS", "").strip(),
                 "project": os.environ.get("OFFICEACE_PROJECT_ID", "").strip(),
                 "base": base}]
    return []


def notify(text, title="OfficeAce 签到"):
    raw = text.encode("utf-8")[:1800].decode("utf-8", "ignore")
    key = os.getenv("QYWX_TOKEN", "").strip() or os.getenv("WECHAT_WEBHOOK", "").strip()
    if key:
        key = key.split("key=")[-1]
        _post_json("https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=" + key,
                   {"msgtype": "text", "text": {"content": title + "\n" + raw}})
    token = os.getenv("PLUSPLUS_TOKEN", "").strip()
    if token:
        _post_json("http://www.pushplus.plus/send",
                   {"token": token, "title": title, "content": raw, "template": "txt"})


def _post_json(url, payload):
    try:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(request, timeout=15).read()
    except Exception as error:
        log("⚠️  推送失败: %s" % error)


def checkin(account):
    credential = Credential(account["ak"], account["sk"], account["sts"], account["project"])
    before = None
    try:
        before = fetch_subscription(credential, account["base"])
    except Exception as error:
        log("   ⚠️ 签到前读数失败（不影响领取）：%s" % error)
    after = claim_bonus(credential, account["base"])
    if before is not None:
        gained = claimed_sum(after) - claimed_sum(before)
        if gained > 0:
            return True, "领取成功：+%s 积分（奖励额度合计 %s）" % (int(gained), int(quota_sum(after)))
        return True, "今天没有可领的奖励（或已领过）"
    return True, "已签到（奖励额度合计 %s）" % int(quota_sum(after))


def main():
    global ONLY, QUERY_ONLY
    args = sys.argv[1:]
    if "--query" in args:
        QUERY_ONLY = True
    if "--only" in args:
        try:
            ONLY = int(args[args.index("--only") + 1])
        except Exception:
            ONLY = None
    accounts = load_accounts()
    if not accounts:
        log("❌ 未配置 OFFICEACE_TOKENS（或 OFFICEACE_AK/OFFICEACE_SK/OFFICEACE_BASE_URL）。")
        log("   每条格式：AK|SK|security_token|project_id|base_url（可加备注在最前）。")
        return 1
    log("╔══════════════════════════════════════════╗")
    log("║ 🏢 OfficeAce 果办 每日签到                ║")
    log("╚══════════════════════════════════════════╝")
    log("👥 账号数: %d" % len(accounts))
    lines = []
    for index, account in enumerate(accounts, 1):
        if ONLY and index != ONLY:
            continue
        log("👤 [%d] %s  AK=%s  base=%s" % (index, account["note"], mask(account["ak"]), account["base"]))
        try:
            if QUERY_ONLY:
                credential = Credential(account["ak"], account["sk"], account["sts"], account["project"])
                subscription = fetch_subscription(credential, account["base"])
                message = "当前奖励额度合计 %s 积分" % int(quota_sum(subscription))
                lines.append("账号%d %s：%s" % (index, account["note"], message))
                log("   %s" % message)
            else:
                ok, message = checkin(account)
                lines.append("%s 账号%d %s：%s" % ("✅" if ok else "❌", index, account["note"], message))
                log("   %s %s" % ("✅" if ok else "❌", message))
        except Exception as error:
            lines.append("账号%d %s：❌ %s" % (index, account["note"], error))
            log("   ❌ 异常: %s" % error)
        time.sleep(1)
    summary = "🏢 OfficeAce 果办每日签到\n" + "\n".join(lines) + "\n🕐 " + time.strftime("%Y-%m-%d %H:%M")
    log(summary)
    if os.getenv("NO_NOTIFY", "").strip() != "1" and lines:
        notify(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())