<div align="center">

<sub><strong>L0NE-6 · DAILY SIGNAL</strong></sub>

# 🏢 OfficeAce Daily

**果办（OfficeAce / OfficeClaw）每日奖励领取工具，内置 V11-HMAC-SHA256 签名与领取前订阅 / claim 回执额度核对。**

[简体中文](README.md) · [English](docs/README.en.md) · [繁體中文](docs/README.zh-Hant.md) · [日本語](docs/README.ja.md) · [한국어](docs/README.ko.md) · [Português (BR)](docs/README.pt-BR.md)

<img src="https://img.shields.io/github/v/release/L0NE-6/OfficeAce-Daily?style=for-the-badge&label=Release&color=2ea44f&logo=github" />
<img src="https://img.shields.io/github/stars/L0NE-6/OfficeAce-Daily?style=for-the-badge&label=Stars&color=FFC75F&logo=github" />
<img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/%E9%9D%92%E9%BE%99-Qinglong-4EAA25?style=for-the-badge" />
<img src="https://img.shields.io/badge/GitHub%20Actions-Supported-2088FF?style=for-the-badge&logo=githubactions&logoColor=white" />
<img src="https://img.shields.io/badge/License-MIT-F472B6?style=for-the-badge" />
<a href="https://github.com/L0NE-6/OfficeAce-Daily/releases"><img src="https://img.shields.io/badge/%E2%AC%87%20Download-Releases-2ea44f?style=for-the-badge&logo=github" /></a>

[✨ 30 秒速览](#-30-秒速览) · [🚀 青龙面板](#-青龙面板) · [☁️ GitHub Actions](#-github-actions) · [🔑 获取凭据](#-获取凭据) · [🔧 环境变量](#-环境变量) · [❓ 常见问题](#-常见问题) · [🚫 使用边界](#usage-policy) · [✦ 星轨](#-星轨-star-trail)

</div>

---

<a id="usage-policy"></a>
## 🚫 使用边界与转载声明

> [!IMPORTANT]
> **官方版本永久免费。** 未经作者书面许可，禁止付费包装、搬运引流、冒充作者，或使用作者身份与二维码制造官方授权假象。违规内容可能被要求下架；作者可暂停更新、归档或删除仓库及相关 Release。

本项目仓库、脚本、部署说明和 Release 下载始终免费公开。未经作者明确书面许可，禁止将本项目包装为付费资源、内部版、独家版、会员权益、收费课程、付费部署或包更新服务；禁止搬运到其他账号、群组、频道、网盘、电商或付费平台进行涨粉、截流、倒卖和引流；禁止删除作者与版权信息后冒充原创；禁止使用作者昵称、头像、二维码和项目名称制造官方授权假象。

> 如需商业合作、品牌授权、联合分发或使用作者名义提供付费服务，请先取得作者明确书面授权。完整规则、收款码防诈骗说明和违规处理方式见 **[NOTICE.md](NOTICE.md)**。

> 官方仓库和 Release 始终免费。第三方以“下载费 / 激活费 / 内部版 / 代部署 / 会员门槛”等名义收费，均与作者无关，请停止付款并保留证据。

> 对上述违规行为，作者有权要求立即停止传播、删除内容并下架相关商品或页面；并可视情况暂停更新、归档或删除本仓库及相关 Release、向平台投诉或采取进一步必要措施。

---

## ✨ 30 秒速览

| 维度 | 说明 |
| :--- | :--- |
| **用途** | 领取果办（OfficeAce / OfficeClaw）当天可用的每日奖励与一次性新人礼。 |
| **输入** | `OFFICEACE_TOKENS`，或 `OFFICEACE_AK` / `OFFICEACE_SK` / `OFFICEACE_STS` / `OFFICEACE_PROJECT_ID` / `OFFICEACE_BASE_URL` 单账号变量。 |
| **输出** | 分账号领取结果、领取前后订阅的额度差值、奖励额度合计与可选企业微信 / PushPlus 推送。 |
| **部署** | 青龙面板、GitHub Actions、Windows / Linux 本地运行。 |
| **依赖** | Python 3.8+，仅使用标准库，无需安装第三方包。 |
| **成功判据** | 领取前后订阅均可核对，且按活动 `current_value` 看到真实增量，或 claim 明确返回空列表表示今日已结算；任一侧读数失败均标记未确认或失败。 |

## ✨ 核心能力

- **一次领取当天奖励**：每日签到与一次性新人礼由同一个 claim 动作下发。
- **V11-HMAC-SHA256**：内置完整签名实现，按区域作用域 `cn-southwest-2/apic` 生成请求。
- **领取对账**：先读 subscription，claim 后重读订阅，用前后活动额度确认实际增量。
- **多账号**：`OFFICEACE_TOKENS` 支持换行或 `&` 分隔。
- **只读核对**：`--query` 只查询订阅与奖励额度，不发起领取。
- **单文件自包含**：青龙只需上传 `officeace_daily.py`。
- **可选推送与日志脱敏**：支持企业微信、PushPlus，日志只显示 AK 的前后片段。

## ⚠️ 凭据寿命

控制面接口使用华为云临时 AK/SK、`security_token` 与 `project_id`。仓库现有文档记录的实测寿命约为 **2 小时**，过期后领取会失败。

| 凭据 | 寿命 | 用途 | 本工具能否从桌面端直接读取 |
| :--- | :--- | :--- | :--- |
| 网关 Basic（`model_app_key:model_app_secret`） | 不过期 | 模型转发 | ✅ `officeace_get_token.py` 可读 |
| 控制面临时 AK/SK + STS + `project_id` | 约 2 小时 | 额度查询与签到 | ❌ 不在该桌面配置中 |

> [!IMPORTANT]
> 网关 Basic 凭据不能单独完成签到。长期无人值守时，需要在脚本外部按上游实际有效期刷新控制面凭据并更新环境变量。

## 🔑 获取凭据

### 读取本机客户端配置

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

### 多账号格式

```text
备注|AK_VALUE|SK_VALUE|STS_VALUE|PROJECT_ID|https://modelgw-xxxx.cn-southwest-2.huaweicloud-agentarts.com/v2
副号|AK_VALUE|SK_VALUE|STS_VALUE|PROJECT_ID|https://modelgw-yyyy.cn-southwest-2.huaweicloud-agentarts.com/v2
```

也可以省略备注，直接使用五段格式：

```text
AK_VALUE|SK_VALUE|STS_VALUE|PROJECT_ID|https://modelgw-xxxx.cn-southwest-2.huaweicloud-agentarts.com/v2
```

脚本至少要求 AK、SK 与 `base_url` 存在；STS 与 `project_id` 是否必须由上游当前接口决定，签到前应先用 `--query` 核对。

## 🚀 青龙面板

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

## 🚀 GitHub Actions

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

## 🔧 环境变量

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

## ⌨️ 命令行参数

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

## 🧪 验证范围

| 项目 | 结果 |
| :--- | :--- |
| 签名对拍 | 6 个官方签名向量逐字节一致，覆盖 SDK / V11、转义路径与查询排序。 |
| 领取增量 | 按 `current_value` 差值计算，离线场景验证了 `+50`。 |
| 幂等 | 重复领取返回今日无可领奖励或已领过。 |
| 临时凭据过期 | 输出明确提示，要求重新导入约 2 小时有效期的控制面凭据。 |
| 多账号与脱敏 | 离线检查通过。 |

> [!NOTE]
> 签名和领取流程已按官方算法与真实向量对拍，但仓库没有提供“真实账号联网领取成功”的证据。首次使用应先运行 `--query`，核对凭据、基址与订阅接口，再执行领取。

## 🔁 领取与成功语义

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

## 🗂️ 数据文件

脚本不落盘控制面凭据。`officeace_get_token.py` 只读取本机 `models.json` 并输出，不写缓存。

| 文件 | 说明 | 是否提交 |
| :--- | :--- | :---: |
| `officeace_tokens.json` | 潜在运行时凭据文件 | ❌ 已忽略 |
| `officeace_result.json` | 潜在运行结果文件 | ❌ 已忽略 |
| `storage.json` / `*accounts*.json` | 本地账号数据 | ❌ 已忽略 |
| `*.log` | 运行日志 | ❌ 已忽略 |

## 🔒 隐私说明

- 仓库不包含真实 AK、SK、STS、`project_id`、账号或手机号。
- 凭据只从环境变量读取，运行时在内存中使用。
- 日志只展示 AK 的前 4 位与后 4 位。
- 不要把 `OFFICEACE_TOKENS`、临时 STS、完整 `models.json` 或未脱敏日志提交到仓库、Issue 或公开 Actions 日志。

## ❓ 常见问题

<details>
<summary><b>为什么能读取 Basic 凭据，签到仍然失败</b></summary>

桌面配置中的 Basic 凭据用于模型网关转发，控制面签到还需要临时 AK/SK、STS 与 `project_id`。这两组凭据用途不同，不能互换。
</details>

<details>
<summary><b>为什么约 2 小时后失效</b></summary>

控制面使用上游签发的临时凭据。脚本不会刷新 OAuth 或 STS 生命周期，因此需要在外部重新获取并更新环境变量。
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

上游仓库将 `schedule:` 保持在注释状态，避免在没有有效临时凭据时空跑。Fork 后如需定时，应取消注释并提供可用的 `OFFICEACE_TOKENS`。
</details>

<details>
<summary><b>如何关闭通知</b></summary>

设置环境变量 `NO_NOTIFY=1`。当前脚本通过该环境变量关闭推送，不需要额外命令行开关。
</details>

## 📦 版本与发布

- 当前发布版：`v1.2.2`（2026-11-12，订阅前后真实增量回读）。
- 历史版本保留在 [Releases](https://github.com/L0NE-6/OfficeAce-Daily/releases)。
- 更新记录见 [CHANGELOG.md](CHANGELOG.md)。

## ⚠️ 免责声明

本项目用于个人学习与自动化实践。请遵守 OfficeAce、OfficeClaw、华为云及相关服务条款，并自行承担账号与服务使用风险。

## ☕ 支持与反馈

遇到问题、发现上游签名或凭据流程变化，欢迎提交 [Issue](https://github.com/L0NE-6/OfficeAce-Daily/issues)。请附上脱敏日志、复现步骤、运行环境和已核对的时间窗口；代码改进可通过 [Pull Request](https://github.com/L0NE-6/OfficeAce-Daily/pulls) 提交。

项目免费开源。如果它节省了你的时间，可以自愿扫码支持；Star、真实运行反馈和文档修正同样重要。

<p align="center">
  <img src="assets/donate-wechat.png" width="260" alt="微信赞赏码" />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="assets/donate-alipay.jpg" width="260" alt="支付宝赞赏码" />
</p>
<p align="center"><sub>💚 微信支付（左） &nbsp;|&nbsp; 💙 支付宝（右，支持信用卡 / 花呗）</sub></p>

> ⚠️ 收款码仅用于向作者自愿赞赏。任何第三方以代下载、代部署、内部资源或会员群为由收费，均与作者无关，请停止付款并保留证据。

---

## ✦ 星轨 Star Trail

> 每颗 Star 都是尘埃落定后的亮点，记录 OfficeAce Daily 在可靠领取与透明报告之间留下的轨迹。

<a href="https://star-history.com/#L0NE-6/OfficeAce-Daily&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=L0NE-6/OfficeAce-Daily&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=L0NE-6/OfficeAce-Daily&type=Date&theme=light" />
    <img alt="OfficeAce Daily Star Trail" src="https://api.star-history.com/svg?repos=L0NE-6/OfficeAce-Daily&type=Date&theme=light" />
  </picture>
</a>

---

<div align="center">
  <a href="https://github.com/L0NE-6/OfficeAce-Daily/releases">Releases</a> ·
  <a href="https://github.com/L0NE-6/OfficeAce-Daily/issues">Issues</a> ·
  <a href="https://github.com/L0NE-6/OfficeAce-Daily">Star</a>
  <br />
  <sub>L0NE-6 · DAILY SIGNAL · 签名有据，回读有数，边界有光</sub>
</div>
