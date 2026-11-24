<div align="center">

<sub><strong>L0NE-6 · DAILY SIGNAL</strong></sub>

# 🏢 OfficeAce Daily

**果办（OfficeAce / OfficeClaw）每日奖励领取工具，内置 V11-HMAC-SHA256 签名与订阅额度回读**

> 当前版本：**v1.2.2**（2026-11-13） · 认证方式：临时 AK / SK / STS / project_id

**[简体中文](README.md)** · [English](docs/README.en.md) · [繁體中文](docs/README.zh-Hant.md) · [日本語](docs/README.ja.md) · [한국어](docs/README.ko.md) · [Português (BR)](docs/README.pt-BR.md)

V11 签名 · 每日奖励 · 订阅回读 · 多账号 · 青龙 · Actions

<img src="https://img.shields.io/badge/Version-v1.2.2-2ea44f?style=for-the-badge&logo=github" alt="Version v1.2.2" />
<img src="https://img.shields.io/github/stars/L0NE-6/OfficeAce-Daily?style=for-the-badge&label=Stars&color=FFC75F&logo=github" alt="Stars" />
<img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.8+" />
<img src="https://img.shields.io/badge/Qinglong-ready-4EAA25?style=for-the-badge" alt="Qinglong" />
<img src="https://img.shields.io/badge/GitHub%20Actions-supported-2088FF?style=for-the-badge&logo=githubactions&logoColor=white" alt="GitHub Actions" />

[边界](#policy) · [速览](#overview) · [协议](#protocol) · [凭据](#credentials) · [快速开始](#quickstart) · [青龙](#qinglong) · [Actions](#actions) · [CLI](#cli) · [结果码](#result-codes) · [成功判据](#success) · [测试](#tests) · [目录](#layout) · [版本](#release) · [赞赏](#donate) · [反馈](#feedback)

</div>

---

<a id="policy"></a>
## 🚫 使用边界

### 🚫 使用边界与转载声明

> [!IMPORTANT]
> **官方版本永久免费。** 未经作者书面许可，禁止付费包装、搬运引流、冒充作者，或使用作者身份与二维码制造官方授权假象。违规内容可能被要求下架；作者可暂停更新、归档或删除仓库及相关 Release。

本项目仓库、脚本、部署说明和 Release 下载始终免费公开。未经作者明确书面许可，禁止将本项目包装为付费资源、内部版、独家版、会员权益、收费课程、付费部署或包更新服务；禁止搬运到其他账号、群组、频道、网盘、电商或付费平台进行涨粉、截流、倒卖和引流；禁止删除作者与版权信息后冒充原创；禁止使用作者昵称、头像、二维码和项目名称制造官方授权假象。

> 如需商业合作、品牌授权、联合分发或使用作者名义提供付费服务，请先取得作者明确书面授权。完整规则、收款码防诈骗说明和违规处理方式见 **[NOTICE.md](NOTICE.md)**。

> 官方仓库和 Release 始终免费。第三方以“下载费 / 激活费 / 内部版 / 代部署 / 会员门槛”等名义收费，均与作者无关，请停止付款并保留证据。

> 对上述违规行为，作者有权要求立即停止传播、删除内容并下架相关商品或页面；并可视情况暂停更新、归档或删除本仓库及相关 Release、向平台投诉或采取进一步必要措施。

---

---

<a id="overview"></a>
## ✨ 30 秒速览

### ✨ 30 秒速览

| 维度 | 说明 |
| :--- | :--- |
| **用途** | 领取果办（OfficeAce / OfficeClaw）当天可用的每日奖励与一次性新人礼。 |
| **输入** | `OFFICEACE_TOKENS`，或 `OFFICEACE_AK` / `OFFICEACE_SK` / `OFFICEACE_STS` / `OFFICEACE_PROJECT_ID` / `OFFICEACE_BASE_URL` 单账号变量。 |
| **输出** | 分账号领取结果、领取前后订阅的额度差值、奖励额度合计与可选企业微信 / PushPlus 推送。 |
| **部署** | 青龙面板、GitHub Actions、Windows / Linux 本地运行。 |
| **依赖** | Python 3.8+，仅使用标准库，无需安装第三方包。 |
| **成功判据** | 领取前后订阅均可核对，且按活动 `current_value` 看到真实增量，或 claim 明确返回空列表表示今日已结算；任一侧读数失败均标记未确认或失败。 |

---

<a id="what"></a>
## 🧭 这是什么

### ✨ 核心能力

- **一次领取当天奖励**：每日签到与一次性新人礼由同一个 claim 动作下发。
- **V11-HMAC-SHA256**：内置完整签名实现，按区域作用域 `cn-southwest-2/apic` 生成请求。
- **领取对账**：先读 subscription，claim 后重读订阅，用前后活动额度确认实际增量。
- **多账号**：`OFFICEACE_TOKENS` 支持换行或 `&` 分隔。
- **只读核对**：`--query` 只查询订阅与奖励额度，不发起领取。
- **单文件自包含**：青龙只需上传 `officeace_daily.py`。
- **可选推送与日志脱敏**：支持企业微信、PushPlus，日志只显示 AK 的前后片段。

---

<a id="protocol"></a>
## 🔁 协议与回读

### 控制面

```http
GET  /v1/subscription
POST /v1/subscription/bonus/claim
```

请求使用 `V11-HMAC-SHA256`，作用域服务为 `apic`，区域默认 `cn-southwest-2`。

### 回读

领取前读取订阅快照，领取后再次读取 `bonus_skus`，按 `used` 增量核对实际新增额度。claim 返回空列表代表当日已结算，不能直接当作新增成功。

---

<a id="credentials"></a>
## 🔑 凭据与账号

| 变量 | 必需 | 说明 |
| :--- | :---: | :--- |
| `OFFICEACE_TOKENS` | 多账号 | `备注|AK|SK|security_token|project_id|base_url` |
| `OFFICEACE_AK` / `OFFICEACE_SK` | 单账号 | 控制面临时签名凭据 |
| `OFFICEACE_STS` | 单账号 | security token |
| `OFFICEACE_PROJECT_ID` | 单账号 | 项目 ID |
| `OFFICEACE_BASE_URL` | 单账号 | 控制面基址 |

`officeace_get_token.py` 只能读取本机网关 Basic 凭据，不能代替控制面临时 AK / SK / STS / project_id。

### ⚠️ 凭据寿命

控制面接口使用华为云临时 AK/SK、`security_token` 与 `project_id`。仓库现有文档记录的实测寿命约为 **2 小时**，过期后领取会失败。

| 凭据 | 寿命 | 用途 | 本工具能否从桌面端直接读取 |
| :--- | :--- | :--- | :--- |
| 网关 Basic（`model_app_key:model_app_secret`） | 不过期 | 模型转发 | ✅ `officeace_get_token.py` 可读 |
| 控制面临时 AK/SK + STS + `project_id` | 约 2 小时 | 额度查询与签到 | ❌ 不在该桌面配置中 |

> [!IMPORTANT]
> 网关 Basic 凭据不能单独完成签到。长期无人值守时，需要在脚本外部按服务端实际有效期刷新控制面凭据并更新环境变量。
### 🔑 获取凭据

#### 读取本机客户端配置

```bash
python officeace_get_token.py
python officeace_get_token.py --list
python officeace_get_token.py --json
python officeace_get_token.py --path <文件或目录>
```

工具默认搜索：

```text
~/.office-claw/.jiuwenclaw/config/routing_state/users/<账号ID>/models.json
```

它兼容两种网关凭据写法：

- `api_key` 直接存储 `key:secret`。
- 凭据位于 `custom_headers` 的 `Authorization: Basic ...`。

工具能输出网关基址、Basic key 与 secret；控制面 STS 与 `project_id` 需要从客户端或控制台的临时凭据流程另外获取。

#### 多账号格式

```text
备注|AK_VALUE|SK_VALUE|STS_VALUE|PROJECT_ID|https://modelgw-xxxx.cn-southwest-2.huaweicloud-agentarts.com/v2
副号|AK_VALUE|SK_VALUE|STS_VALUE|PROJECT_ID|https://modelgw-yyyy.cn-southwest-2.huaweicloud-agentarts.com/v2
```

也可以省略备注，直接使用五段格式：

```text
AK_VALUE|SK_VALUE|STS_VALUE|PROJECT_ID|https://modelgw-xxxx.cn-southwest-2.huaweicloud-agentarts.com/v2
```

脚本至少要求 AK、SK 与 `base_url` 存在；STS 与 `project_id` 是否必须由服务端当前接口决定，签到前应先用 `--query` 核对。

---

<a id="quickstart"></a>
## 🚀 快速开始

### ❓ 常见问题

<details>
<summary><b>为什么能读取 Basic 凭据，签到仍然失败</b></summary>

桌面配置中的 Basic 凭据用于模型网关转发，控制面签到还需要临时 AK/SK、STS 与 `project_id`。这两组凭据用途不同，不能互换。
</details>

<details>
<summary><b>为什么约 2 小时后失效</b></summary>

控制面使用服务端签发的临时凭据。脚本不会刷新 OAuth 或 STS 生命周期，因此需要在外部重新获取并更新环境变量。
</details>

<details>
<summary><b>如何先做只读核对</b></summary>

```bash
python officeace_daily.py --query
```

该命令只读取订阅，不执行 claim。确认基址与额度正常后再运行无参数命令。
</details>

<details>
<summary><b>Actions 为什么默认不自动运行</b></summary>

本仓库将 `schedule:` 保持在注释状态，避免在没有有效临时凭据时空跑。Fork 后如需定时，应取消注释并提供可用的 `OFFICEACE_TOKENS`。
</details>

<details>
<summary><b>如何关闭通知</b></summary>

设置环境变量 `NO_NOTIFY=1`。当前脚本通过该环境变量关闭推送，不需要额外命令行开关。
</details>

---

<a id="qinglong"></a>
## 🐧 青龙面板

### 🚀 青龙面板

1. 将 `officeace_daily.py` 上传到青龙脚本目录。
2. 在环境变量中添加 `OFFICEACE_TOKENS`。
3. 新建定时任务，从脚本列表生成：

   ```bash
   task officeace_daily.py
   ```

建议 cron：

```cron
10 9 * * *
```

青龙按面板本地时间解释 cron。使用裸 `python` 启动时，面板环境变量不一定会注入；定时任务优先使用青龙运行器。

---

<a id="actions"></a>
## ☁️ GitHub Actions

### 🚀 GitHub Actions

仓库内置 [`.github/workflows/daily.yml`](.github/workflows/daily.yml)，当前 `schedule:` 默认注释，只保留 `workflow_dispatch` 手动触发。

| Secret | 对应变量 | 必填 | 说明 |
| :--- | :--- | :---: | :--- |
| `OFFICEACE_TOKENS` | `OFFICEACE_TOKENS` | ✅ | 多账号临时控制面凭据。 |
| `QYWX_TOKEN` | `QYWX_TOKEN` | ➖ | 企业微信机器人 key。 |
| `PLUSPLUS_TOKEN` | `PLUSPLUS_TOKEN` | ➖ | PushPlus token。 |

进入 **Actions → OfficeAce Daily → Run workflow** 手动验证。需要定时时，自行取消工作流中的两行注释：

```yaml
schedule:
  - cron: '10 1 * * *'
```

`10 1 * * *` 使用 UTC，对应北京时间每天 09:10。由于控制面凭据大约 2 小时失效，Actions 定时执行前必须确保证书 Secret 仍然有效；仅配置长期 Basic 凭据不会让签到自动变得可运行。

---

<a id="cli"></a>
## ⌨️ CLI 与环境变量

### 🔧 环境变量

| 变量 | 必填 | 说明 |
| :--- | :---: | :--- |
| `OFFICEACE_TOKENS` | 多账号 ✅ | 多账号，换行或 `&` 分隔；每条五段或六段。 |
| `OFFICEACE_AK` | ➖ | 单账号兜底 Access Key。 |
| `OFFICEACE_SK` | ➖ | 单账号兜底 Secret Key。 |
| `OFFICEACE_STS` | ➖ | 单账号兜底 `security_token`。 |
| `OFFICEACE_PROJECT_ID` | ➖ | 单账号兜底 `project_id`。 |
| `OFFICEACE_BASE_URL` | ➖ | 单账号兜底网关基址，通常以 `/v2` 结尾。 |
| `OFFICEACE_CLIENT_DIR` | ➖ | 本机凭据读取工具的搜索根目录。 |
| `QYWX_TOKEN` | ➖ | 企业微信机器人 key；也兼容 `WECHAT_WEBHOOK`。 |
| `PLUSPLUS_TOKEN` | ➖ | PushPlus token。 |
| `NO_NOTIFY` | ➖ | 设为 `1` 关闭推送。 |

`OFFICEACE_TOKENS` 非空时优先于单账号变量。
### ⌨️ 命令行参数

| 参数 | 作用 |
| :--- | :--- |
| （无） | 为全部账号执行领取。 |
| `--only N` | 只运行第 N 个账号。 |
| `--query` | 只读查询当前额度，不发起领取。 |

关闭推送使用环境变量 `NO_NOTIFY=1`。

凭据读取工具的独立参数：

| 参数 | 作用 |
| :--- | :--- |
| `--path PATH` | 指定 `models.json`、所在目录或搜索根目录。 |
| `--list` | 只列出找到的配置文件。 |
| `--json` | 输出机器可读 JSON。 |

---

<a id="result-codes"></a>
## 🚦 结果码

| 状态 | 含义 |
| :--- | :--- |
| 实际增量大于 0 | 领取成功 |
| claim 空列表 | 当日已结算，中性结果 |
| 凭据缺失或过期 | 失败，需要更新控制面凭据 |
| 签名 / 权限错误 | 失败，检查区域、project_id 与临时凭据 |
| 回读异常 | 不能宣称成功 |

---

<a id="success"></a>
## ✅ 成功判据

成功判据是领取前后的订阅快照可读，并且 `bonus_skus.used` 出现实际增量；仅有 claim HTTP 成功不算完成。

### 🔁 领取与成功语义

```text
GET  /v1/subscription             # 领取前基线
POST /v1/subscription/bonus/claim # 触发当天结算
GET  /v1/subscription             # 领取后回读，用于增量核对
```

- 每日签到与一次性新人礼由服务端同一次动作下发。
- 当天已领取时按幂等处理，不重复计分。
- 领取前后订阅都可读取时，按活动 `current_value` 报告实际增量。
- claim 明确返回空列表时，显示“今日无可领奖励或已领过”。
- 领取前或领取后订阅读数失败时，脚本标记“结果未确认”，不会声称领取成功。
- 单个账号异常不会阻止其余账号继续执行。

---

<a id="tests"></a>
## 🧪 测试

```powershell
$env:PYTHONUTF8 = "1"
python -m unittest discover -s tests -v
python -m py_compile officeace_daily.py officeace_get_token.py
```

测试覆盖签名、账号解析与领取回读；临时控制面凭据仍需单独验证。

### 🧪 验证范围

| 项目 | 结果 |
| :--- | :--- |
| 签名对拍 | 6 个官方签名向量逐字节一致，覆盖 SDK / V11、转义路径与查询排序。 |
| 领取增量 | 按 `current_value` 差值计算，离线场景验证了 `+50`。 |
| 幂等 | 重复领取返回今日无可领奖励或已领过。 |
| 临时凭据过期 | 输出明确提示，要求重新导入约 2 小时有效期的控制面凭据。 |
| 多账号与脱敏 | 离线检查通过。 |

> [!NOTE]
> 签名和领取流程已按官方算法与真实向量对拍，但仓库没有提供“真实账号联网领取成功”的证据。首次使用应先运行 `--query`，核对凭据、基址与订阅接口，再执行领取。

---

<a id="design"></a>
## 🧱 设计原则

- 标准库实现，减少青龙环境依赖。
- V11 签名与领取流程分离，便于测试。
- 先查订阅，再 claim，再回读实际增量。
- 临时凭据不自动伪造，不把查询工具当作控制面凭据来源。

---

<a id="privacy"></a>
## 🔒 隐私与安全

凭据、状态文件、日志与运行缓存都属于账号级数据。仓库和 Issue 中只保留脱敏片段。

### 🔒 隐私说明

- 仓库不包含真实 AK、SK、STS、`project_id`、账号或手机号。
- 凭据只从环境变量读取，运行时在内存中使用。
- 日志只展示 AK 的前 4 位与后 4 位。
- 不要把 `OFFICEACE_TOKENS`、临时 STS、完整 `models.json` 或未脱敏日志提交到仓库、Issue 或公开 Actions 日志。

---

<a id="layout"></a>
## 📁 目录结构

### 🗂️ 数据文件

脚本不落盘控制面凭据。`officeace_get_token.py` 只读取本机 `models.json` 并输出，不写缓存。

| 文件 | 说明 | 是否提交 |
| :--- | :--- | :---: |
| `officeace_tokens.json` | 潜在运行时凭据文件 | ❌ 已忽略 |
| `officeace_result.json` | 潜在运行结果文件 | ❌ 已忽略 |
| `storage.json` / `*accounts*.json` | 本地账号数据 | ❌ 已忽略 |
| `*.log` | 运行日志 | ❌ 已忽略 |

---

<a id="release"></a>
## 📦 版本与发布

当前标签为 `v1.2.2`。发布前确认签名契约、回读测试、README 变量表与 Actions Secrets 同步。

### 📦 版本与发布

- 当前发布版：`v1.2.2`（2026-11-12，订阅前后真实增量回读）。
- 历史版本保留在 [Releases](https://github.com/L0NE-6/OfficeAce-Daily/releases)。
- 更新记录见 [CHANGELOG.md](CHANGELOG.md)。

---

<a id="disclaimer"></a>
## ⚠️ 免责声明

仓库内容用于账号持有人维护自身权益。使用前应确认账号、服务条款与所在地规则；作者不对账号限制、接口变化、网络失败或第三方部署造成的损失作出保证。

完整展示与转载规则见 [NOTICE.md](NOTICE.md)。

---

<a id="donate"></a>
## ☕ 赞赏码

### 支持与投喂

如果这个项目节省了你的时间，可以扫码支持维护。赞赏完全自愿，不影响代码、文档与 Issue 处理。

<div align="center">
<table>
<tr>
<td align="center"><strong>微信赞赏码</strong><br /><img src="assets/donate-wechat.png" width="260" alt="微信赞赏码" /></td>
<td align="center"><strong>支付宝赞赏码</strong><br /><img src="assets/donate-alipay.jpg" width="260" alt="支付宝赞赏码" /></td>
</tr>
</table>
</div>

---

<a id="feedback"></a>
## 💬 反馈与 Star History

### 反馈与贡献

- [提交 Issue](https://github.com/L0NE-6/OfficeAce-Daily/issues)
- [提交 Pull Request](https://github.com/L0NE-6/OfficeAce-Daily/pulls)
- [查看更新日志](CHANGELOG.md)

反馈请附脱敏日志、复现步骤、运行环境与实际结果。不要贴 Token、Cookie、JWT、手机号或运行状态文件。

<a href="https://star-history.com/#L0NE-6/OfficeAce-Daily&Date">
  <img src="https://api.star-history.com/svg?repos=L0NE-6/OfficeAce-Daily&type=Date" alt="OfficeAce-Daily Star History" />
</a>
