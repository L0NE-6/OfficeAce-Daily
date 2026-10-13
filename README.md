<div align="center">

# 🏢 OfficeAce Daily

**果办（OfficeAce / OfficeClaw）每日签到脚本 · 单文件自包含 · V11 签名 · 多账号**

<img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/%E9%9D%92%E9%BE%99%E9%9D%A2%E6%9D%BF-%E5%8D%95%E6%96%87%E4%BB%B6%E8%BF%90%E8%A1%8C-4EAA25?style=flat-square" />
<img src="https://img.shields.io/badge/GitHub%20Actions-%E6%94%AF%E6%8C%81-2088FF?style=flat-square&logo=githubactions&logoColor=white" />
<img src="https://img.shields.io/badge/License-MIT-F472B6?style=flat-square" />

</div>

---

## ✨ 这是什么

一个脚本领取果办（华为云 OfficeAce / OfficeClaw）的**每日奖励积分**：

```text
读订阅（领取前）  GET  /v1/subscription                    ← V11-HMAC-SHA256 签名
领取奖励          POST /v1/subscription/bonus/claim  body {}  ← 一次领当天全部
读订阅（领取后）  GET  /v1/subscription                    ← 算增量，如实报数
```

- 🎯 **一次领完**：每日签到与一次性新人礼在服务端是**同一个动作**，一次调用把当天所有可领奖励发下来；
- 🔁 **接口幂等**：一天一个活动只能领一次，重复领不报错（返回同一份列表），所以重复跑是安全的空动作；
- 🔐 **V11-HMAC-SHA256 签名**：控制面接口按区域作用域 `cn-southwest-2/apic` 签名，官方 6 个签名向量逐字节对拍一致；
- 📊 **如实报增量**：按 `current_value` 差值报「+N 积分」，读不到增量时说「已签到」，不编数字；
- 👥 多账号、企业微信 / PushPlus 推送、日志脱敏。

> 📦 **单文件自包含**：`officeace_daily.py` 里内置了完整签名实现，青龙上传一个文件就能跑，不需要任何配套模块。
> ⬇️ **不想用 git？** 直接到 **[Releases](https://github.com/L0NE-6/OfficeAce-Daily/releases)** 下载完整包 zip 或单个脚本，每个包都附 SHA256 校验值。

---

## ⚠️ 凭据 2 小时过期（先看这条）

控制面接口用的是华为云**临时 AK/SK + security_token + project_id**，实测 **约 2 小时有效**。
过期后签到会失败并明确提示：

```text
控制面凭据已失效（临时 AK/SK 约 2 小时过期）——请重新从客户端/控制台导入一次
```

这**是上游的凭据寿命，不是脚本限制** —— 上游自己也只发这种临时凭据。

| 凭据 | 寿命 | 用途 | 本工具能否读取 |
| :--- | :--- | :--- | :--- |
| 网关 Basic（`model_app_key:model_app_secret`） | **不过期** | 模型转发 | ✅ `officeace_get_token.py` 可读 |
| 控制面临时 AK/SK + STS + project_id | **约 2 小时** | 额度 / 签到 | ❌ 不落盘，需另外导入 |

> 需要长期无人值守时，建议在本机按 2 小时节奏刷新凭据后写入青龙环境变量；
> 脚本本身就是一次性调用，不需要常驻进程。

---

## 🚀 部署方式一：青龙面板（三步）

| 步骤 | 做什么 |
| :--- | :--- |
| **1️⃣ 上传脚本** | 把 `officeace_daily.py` 放到脚本目录 |
| **2️⃣ 配置变量** | 环境变量里添加 `OFFICEACE_TOKENS`（见下方格式） |
| **3️⃣ 建定时任务** | 命令填 `task officeace_daily.py`，建议 cron `10 9 * * *` |

> 🐧 **命令必须用青龙运行器**：定时任务里从脚本列表选 `officeace_daily.py`（生成 `task xxx.py`），
> 不要填裸 `python officeace_daily.py` —— 裸调用不会注入面板环境变量。

```
# 多账号：每条一行，`备注|AK|SK|security_token|project_id|base_url`
OFFICEACE_TOKENS=主号|AKxxxx|SKxxxx|STxxxx|项目ID|https://modelgw-xxxx.cn-southwest-2.huaweicloud-agentarts.com/v2
副号|AKyyyy|SKyyyy|STyyyy|项目ID|https://modelgw-yyyy.cn-southwest-2.huaweicloud-agentarts.com/v2
```

---

## ☁️ 部署方式二：GitHub Actions（零服务器）

### 第 1 步：添加 Secrets（仓库 → Settings → Secrets and variables → Actions）

| Secret | 对应环境变量 | 必填 | 说明 |
| :--- | :--- | :---: | :--- |
| `OFFICEACE_TOKENS` | `OFFICEACE_TOKENS` | ✅ | 多账号凭据（同上格式） |
| `QYWX_TOKEN` | `QYWX_TOKEN` | ⬜ | 企业微信机器人 key |
| `PLUSPLUS_TOKEN` | `PLUSPLUS_TOKEN` | ⬜ | PushPlus token |

### 第 2 步：开启 Actions

仓库 → **Actions** → 选择 **OfficeAce Daily** → **Enable workflow**。

### 第 3 步：手动跑一次验证

**Actions** → **OfficeAce Daily** → **Run workflow**（默认仅手动触发；工作流里 `schedule:` 两行取消注释即可开启定时）。

---

## 🔑 本机凭据读取工具

桌面端登录后，配置就落在本机，不用手抄：

```bash
python officeace_get_token.py            # 读取并打印 BASE_URL / AK / SK
python officeace_get_token.py --list     # 只列出找到的账号配置
python officeace_get_token.py --json     # 机器可读输出
python officeace_get_token.py --path <文件或目录>   # 指定位置
```

默认搜索 `~/.office-claw/.jiuwenclaw/config/routing_state/users/<账号ID>/models.json`，并自动兼容两种写法：
`api_key` 直接是 `key:secret`，或凭据藏在 `custom_headers` 的 `Authorization: Basic …` 里。

| 能取到 | 取不到 |
| :--- | :--- |
| ✅ `api_base`（网关基址） | ❌ 控制面临时 AK/SK/STS |
| ✅ 网关 Basic 凭据（key/secret） | ❌ `project_id` |

> 签到用的控制面凭据是 OAuth 换来的临时凭据、**不在这份配置里**，仍需从客户端/控制台另外导入（约 2 小时过期）。
> 本工具解决的是「网关基址和 Basic 凭什么写」这一步 —— 那也最容易抄错。

---

## ⌨️ 命令行参数

| 参数 | 作用 |
| :--- | :--- |
| （无） | 所有账号领取每日奖励 |
| `--only N` | 只跑第 N 个账号（从 1 起） |
| `--query` | **只读**查询积分与奖励活动，不发起领取 |
| `--no-notify` / `NO_NOTIFY=1` | 只打印，不推送 |

```bash
python officeace_daily.py             # 全量领取
python officeace_daily.py --only 1    # 单账号
python officeace_daily.py --query     # 只读核对
```

---

## 🔧 环境变量

| 变量 | 必填 | 说明 |
| :--- | :---: | :--- |
| `OFFICEACE_TOKENS` | ✅ | 多账号，换行或 `&` 分隔；每条 `AK\|SK\|security_token\|project_id\|base_url`，可在最前加备注 |
| `OFFICEACE_AK` | ➖ | 单账号兜底：Access Key |
| `OFFICEACE_SK` | ➖ | 单账号兜底：Secret Key |
| `OFFICEACE_STS` | ➖ | 单账号兜底：security_token（视上游而定，可为空） |
| `OFFICEACE_PROJECT_ID` | ➖ | 单账号兜底：project_id |
| `OFFICEACE_BASE_URL` | ➖ | 单账号兜底：网关基址（形如 `https://host/v2`） |
| `OFFICEACE_CLIENT_DIR` | ➖ | 本机凭据读取工具的搜索根目录 |
| `QYWX_TOKEN` | ➖ | 企业微信机器人 key（也兼容 `WECHAT_WEBHOOK`） |
| `PLUSPLUS_TOKEN` | ➖ | PushPlus token |
| `NO_NOTIFY` | ➖ | 设 `1` 关闭推送 |

---

## 🧪 验证情况

| 项目 | 结果 |
| :--- | :--- |
| 签名对拍 | 官方 **6 个签名向量**（SDK / V11、含转义路径与查询排序、V11 派生密钥按小写十六进制字符串参与 HMAC）**逐字节一致** |
| 领取增量 | 按 `current_value` 差值，自测 +50 场景通过 |
| 幂等 | 重复领取返回「今天没有可领的奖励（或已领过）」 |
| 凭据过期 | 明确提示「约 2 小时过期，请重新导入」 |
| 多账号 / 脱敏 / GBK 控制台 | 均通过 |

> ⚠️ 诚实边界：签名与流程是**按官方算法与真实向量对拍**验证的，但**没有用真实账号联网跑过**——
> 上游凭据每 2 小时过期，首次使用请先用 `--query` 只读核对一次。

---

## 🗂️ 数据文件说明

脚本**不落盘任何凭据**：

- 所有凭据只从环境变量读取，运行时在内存中使用，不写文件；
- `officeace_get_token.py` 只**读**本机配置并打印，不写任何缓存；
- `.gitignore` 已屏蔽 `officeace_tokens.json` / `officeace_result.json` 等潜在运行时文件。

---

## 📊 推送报告示例

```text
🏢 OfficeAce 果办每日签到
✅ 账号1 主号：领取成功：+100 积分（奖励额度合计 150）
✅ 账号2 副号：今天没有可领的奖励（或已领过）
🕐 2026-10-13 09:10
```

---

## 📁 目录结构

```text
OfficeAce-Daily/
├── officeace_daily.py          # 每日签到（内置 V11 签名，单文件自包含）
├── officeace_get_token.py      # 本机凭据读取工具
├── requirements.txt            # 依赖说明（实际零第三方依赖）
├── README.md
├── CHANGELOG.md
├── LICENSE
├── .gitignore
├── assets/                     # 收款码等素材
└── .github/workflows/daily.yml # Actions 工作流（默认手动触发）
```

---

## 📦 版本与发布

- 每次更新单独发一个 Release：`v1.0.0` → `v1.1.0` …，历史版本保留可下载；
- 每个 Release 附：完整包 zip + 各脚本单文件 + `SHA256SUMS.txt`；
- 下载页：<https://github.com/L0NE-6/OfficeAce-Daily/releases>

---

## 🔒 隐私说明

脚本**不含任何账号、AK/SK、Cookie 或设备信息**，所有凭据均由环境变量（或 GitHub Secrets）注入。
日志只打印 AK 的**前 4 位与后 4 位**，不会输出完整凭据。

---

## ⚠️ 免责声明

本项目仅供 **学习与个人自动化** 使用。请遵守 OfficeAce / 华为云的服务条款，使用风险自负。

---

## ☕ 支持与投喂

脚本是**完全免费、无广告、无任何功能限制**的（本仓库与发布包也不含你的任何数据）。
如果它确实帮你省了时间、多领了积分，欢迎请我喝杯咖啡 —— **纯自愿，不影响任何功能**，也不影响我在 Issue 里的响应速度 🙌

<p align="center">
  <img src="assets/donate-wechat.png" width="260" alt="微信赞赏码" />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="assets/donate-alipay.jpg" width="260" alt="支付宝收款码" />
</p>
<p align="center"><sub>💚 微信支付（左） &nbsp;|&nbsp; 💙 支付宝（右，支持信用卡 / 花呗）</sub></p>

> 💡 **不花钱也能帮上很多忙**：点个 ⭐ Star、提一个带日志的 Issue、发一个 Pull Request、或者把脚本分享给需要的朋友 —— 这些同样是最好的支持。

---

## 💬 反馈与贡献

遇到问题、有功能建议，或者发现了更好的实现方式，欢迎：

- 提交 [Issue](https://github.com/L0NE-6/OfficeAce-Daily/issues) —— 报 bug、提需求
- 发起 [Pull Request](https://github.com/L0NE-6/OfficeAce-Daily/pulls) —— 直接贡献代码

> 提 Issue 时如果能附上**运行日志**和**复现步骤**，定位会快很多 🙏

---

<div align="center">
  <sub>🏢 如果这个脚本帮到你，点个 <b>Star</b> 支持一下，或者到 <a href="#-支持与投喂">支持与投喂</a> 请我喝杯咖啡 ✨</sub>
</div>
