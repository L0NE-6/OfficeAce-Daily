<div align="center">

# 🏢 OfficeAce Daily

**华为云果办（OfficeAce / OfficeClaw）每日签到 · 单文件青龙脚本 · 多账号**

<img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/%E9%9D%92%E9%BE%99%E9%9D%A2%E6%9D%BF-%E5%8D%95%E6%96%87%E4%BB%B6%E8%BF%90%E8%A1%8C-4EAA25?style=flat-square" />
<img src="https://img.shields.io/badge/License-MIT-F472B6?style=flat-square" />

</div>

---

## ✨ 这是什么

一个脚本领取果办「奖励积分」的每日奖励：**每日签到 + 一次性新人礼**在服务端是同一个动作 ——
`POST /v1/subscription/bonus/claim` 一次把当天所有可领的奖励发下来，接口幂等（重复领不报错、返回同一份列表）。

- 🔐 控制面签名：**V11-HMAC-SHA256**（区域作用域 `cn-southwest-2/apic`）
- 📊 领取前后各读一次订阅，按 `current_value` 差值如实报「+N 积分」
- 🔁 多账号、企业微信 / PushPlus 推送、日志脱敏

---

## ⚠️ 凭据 2 小时过期（先看这条）

控制面接口用的是**华为云临时 AK/SK + security_token + project_id**，实测 **约 2 小时有效**。
过期后签到会失败并提示：

```
控制面凭据已失效（临时 AK/SK 约 2 小时过期）——请重新从客户端/控制台导入一次
```

拿到这组临时凭据的两条路：

1. **桌面端**：登录果办客户端，从
   `~/.office-claw/.jiuwenclaw/config/routing_state/users/<账号ID>/` 下的配置取 `api_base` 与签名凭据；
2. **控制台导入**：按客户端形态导入一份，把 AK/SK/STS/project_id/base_url 填进环境变量。

> 这是上游的凭据寿命，不是脚本限制：上游自己没有「不过期的控制面凭据」。
> 需要长期无人值守时，建议按 2 小时节奏由本机脚本刷新后写入青龙变量。

---

## 🚀 快速开始

### 1. 配置环境变量（青龙）

| 变量 | 说明 |
| :--- | :--- |
| `OFFICEACE_TOKENS` | 多账号，换行或 `&` 分隔；每条 `AK\|SK\|security_token\|project_id\|base_url`，可加备注在最前 |
| `OFFICEACE_AK` / `OFFICEACE_SK` | 单账号兜底 |
| `OFFICEACE_STS` / `OFFICEACE_PROJECT_ID` | 单账号兜底（project_id 必填，security_token 视上游而定） |
| `OFFICEACE_BASE_URL` | 单账号兜底，形如 `https://modelgw-xxxx.officeace.cn-southwest-2.huaweicloud-agentarts.com/v2` |
| `QYWX_TOKEN` | 企业微信机器人（也兼容 `WECHAT_WEBHOOK`） |
| `PLUSPLUS_TOKEN` | PushPlus |
| `NO_NOTIFY` | 设 `1` 关闭推送 |

### 2. 定时任务

```cron
10 9 * * * python officeace_daily.py
```

### 3. 常用参数

```bash
python officeace_daily.py             # 全部账号领奖励
python officeace_daily.py --only 1    # 只跑第 1 个
python officeace_daily.py --query     # 只读查询额度，不领取
```

---

## 🧪 验证情况

- **签名逐字节对拍**：官方 6 个签名向量（SDK / V11、含路径转义与查询排序、`V11` 派生密钥按小写十六进制字符串参与 HMAC）全部一致；
- 签到链路：领取增量（`current_value` 口径）、幂等重复领取、凭据过期可读报错、多账号解析、日志脱敏；GBK 控制台下日志不崩。

---

## 🔒 隐私说明

- 脚本不收集、不上传任何信息，所有请求直达官方接口；
- 凭据只从环境变量读取，不落盘；
- 日志只打印 AK 的前 4 / 后 4 位。

---

## 📄 License

MIT