# 更新日志

## v1.2.0（2026-10-13）

- 文档补齐：README 按仓库家族统一规格重写（新增部署方式、环境变量总表、参数表、验证情况、数据文件说明、推送示例、目录结构、版本与发布、隐私说明、免责声明、支持与投喂、反馈与贡献等章节）。
- 新增：`assets/` 收款码（微信 / 支付宝）与「支持与投喂」板块。
- 新增：`requirements.txt`（说明实际零第三方依赖）。

## v1.1.0（2026-10-13）

- 新增：本机凭据读取工具 `officeace_get_token.py` —— 自动定位桌面端的 `models.json`，
  读出网关基址与 Basic 凭据（兼容 `api_key` 的 `key:secret` 写法与 `custom_headers` 里的
  `Authorization: Basic …`），直接输出可填进青龙的 `OFFICEACE_BASE_URL` / `OFFICEACE_AK` / `OFFICEACE_SK`；
  支持 `--list` / `--json` / `--path`。
- 说明：控制面临时 AK/SK/STS 不落在该配置里，签到仍需另外导入（约 2 小时过期）。

## v1.0.0（2026-10-13）

- 首个公开版本：果办（OfficeAce / OfficeClaw）每日奖励领取（每日签到 + 一次性新人礼同一动作）。
- 控制面 **V11-HMAC-SHA256** 签名（区域作用域 apic），6 个官方签名向量逐字节对拍通过。
- 领取前后读订阅、按 `current_value` 差值如实报增量；接口幂等，重复领不报错。
- 多账号、`--only` / `--query`、企业微信与 PushPlus 推送、日志脱敏、GBK 控制台安全。