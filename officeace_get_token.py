#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔑 OfficeAce 果办 · 本机凭据读取工具

从本机果办桌面端的配置文件里读出**模型网关基址**与**网关 Basic 凭据**，
直接生成可以填进青龙 `OFFICEACE_*` 的形态。

读哪里
  默认：`~/.office-claw/.jiuwenclaw/config/routing_state/users/<账号ID>/models.json`
  也支持用 `--path` 指定文件 / 目录，或用 `OFFICEACE_CLIENT_DIR` 指定根目录。

能取到什么 / 取不到什么
  ✅ api_base（网关基址，形如 https://host/v2）
  ✅ 网关 Basic 凭据（models.json 的 `api_key` 通常是 `key:secret`；配 `custom_headers`
     里带 `Authorization: Basic …` 时会自动解码成 key/secret）
  ❌ 控制面临时 AK/SK/STS —— 那组是 OAuth 换来的、不落在这份配置里，
     签到要用它，需要从客户端/控制台另外导入（且约 2 小时过期）。

用法
  python officeace_get_token.py                     # 读取并打印
  python officeace_get_token.py --list              # 只列出本机找到的账号目录
  python officeace_get_token.py --path <文件或目录> # 指定位置
  python officeace_get_token.py --json              # 机器可读输出

输出示例
  OFFICEACE_BASE_URL=https://modelgw-xxxx...../v2
  OFFICEACE_AK=<key>          # 网关凭据（转发用，不过期）
  OFFICEACE_SK=<secret>

⚠️ 控制面（签到）还需要 OFFICEACE_STS 与 OFFICEACE_PROJECT_ID，本工具不提供。
"""

import argparse
import base64
import json
import os
import sys

FIELD_BASE = ("api_base", "apiBase", "base_url", "baseUrl")
FIELD_KEY = ("api_key", "apiKey", "modelAppKey", "appKey")
FIELD_SECRET = ("api_secret", "apiSecret", "modelAppSecret", "appSecret")


def log(msg):
    print(msg, flush=True)


def first_text(entry, names):
    for name in names:
        value = entry.get(name)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def decode_basic(value):
    """`Basic xxx` → (key, secret)；解不出返回 ("", "")。"""
    text = (value or "").strip()
    if not text.lower().startswith("basic "):
        return "", ""
    try:
        raw = base64.b64decode(text.split(None, 1)[1].strip()).decode("utf-8", "replace")
    except Exception:
        return "", ""
    if ":" not in raw:
        return "", ""
    key, secret = raw.split(":", 1)
    return key.strip(), secret.strip()


def split_key_secret(value):
    """`key:secret` → (key, secret)；没有冒号时整串当 key。"""
    text = (value or "").strip()
    if ":" in text:
        key, secret = text.split(":", 1)
        return key.strip(), secret.strip()
    return text, ""


def extract_entry(entry):
    """从一条模型记录里取 (base, key, secret)。"""
    base = first_text(entry, FIELD_BASE)
    key = first_text(entry, FIELD_KEY)
    secret = first_text(entry, FIELD_SECRET)
    if key and not secret:
        key, secret = split_key_secret(key)
    headers = entry.get("custom_headers") or entry.get("customHeaders") or {}
    if isinstance(headers, dict):
        for name, value in headers.items():
            if str(name).lower() == "authorization":
                h_key, h_secret = decode_basic(value)
                if h_key:
                    key, secret = h_key, h_secret
    return base, key, secret


def extract_file(path):
    """从一份 models.json 里取 (base, key, secret)，取不到返回 None。"""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as error:
        log("⚠️  读取失败 %s：%s" % (path, error))
        return None
    entries = None
    if isinstance(data, list):
        entries = data
    elif isinstance(data, dict):
        for name in ("models", "data", "items"):
            if isinstance(data.get(name), list):
                entries = data[name]
                break
        if entries is None:
            entries = [data]
    for entry in entries or []:
        if not isinstance(entry, dict):
            continue
        base, key, secret = extract_entry(entry)
        if base or key:
            return base, key, secret
    return None


def candidate_files(root=None):
    """本机可能的 models.json 列表（按账号目录）。"""
    if root:
        if os.path.isfile(root):
            return [root]
        bases = [root]
    else:
        home = os.path.expanduser("~")
        bases = [
            os.path.join(home, ".office-claw", ".jiuwenclaw", "config", "routing_state", "users"),
            os.path.join(home, ".office-claw", "config", "routing_state", "users"),
            os.path.join(home, ".jiuwenclaw", "config", "routing_state", "users"),
        ]
    found = []
    for base in bases:
        if not os.path.isdir(base):
            continue
        direct = os.path.join(base, "models.json")
        if os.path.isfile(direct):
            found.append(direct)
        for name in sorted(os.listdir(base)):
            sub = os.path.join(base, name)
            if os.path.isdir(sub):
                path = os.path.join(sub, "models.json")
                if os.path.isfile(path):
                    found.append(path)
    return found


def main():
    parser = argparse.ArgumentParser(description="读取本机果办客户端凭据")
    parser.add_argument("--path", default=os.environ.get("OFFICEACE_CLIENT_DIR", "").strip(),
                        help="models.json 文件或所在目录 / 根目录")
    parser.add_argument("--list", action="store_true", help="只列出找到的配置文件")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出")
    args = parser.parse_args()

    files = candidate_files(args.path or None)
    if not files:
        log("❌ 没找到果办客户端的 models.json。")
        log("   确认已安装并登录果办客户端，或用 --path 指定文件/目录。")
        return 1
    if args.list:
        for path in files:
            log(path)
        return 0

    results = []
    for path in files:
        parsed = extract_file(path)
        if not parsed:
            continue
        base, key, secret = parsed
        results.append({"path": path, "base": base, "key": key, "secret": secret})

    if not results:
        log("❌ 找到了配置文件，但里面没有可用的网关基址/凭据。")
        return 1

    if args.json:
        log(json.dumps(results, ensure_ascii=False, indent=2))
        return 0

    for item in results:
        log("=" * 64)
        log("📄 %s" % item["path"])
        log("=" * 64)
        if item["base"]:
            log("OFFICEACE_BASE_URL=%s" % item["base"])
        if item["key"]:
            log("OFFICEACE_AK=%s" % item["key"])
        if item["secret"]:
            log("OFFICEACE_SK=%s" % item["secret"])
        log("")
    log("ℹ️  以上是网关凭据（转发用、不过期）。")
    log("   签到还需要控制面的 OFFICEACE_STS 与 OFFICEACE_PROJECT_ID ——")
    log("   那组是 OAuth 换来的临时凭据，不在这份配置里，请从客户端/控制台另外导入。")
    return 0


if __name__ == "__main__":
    sys.exit(main())