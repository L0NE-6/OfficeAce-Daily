# 🏢 OfficeAce Daily

**果辦（OfficeAce / OfficeClaw）每日獎勵領取工具，內建 V11-HMAC-SHA256 簽名與訂閱額度回讀。**

[简体中文](../README.md) | [English](README.en.md) | [繁體中文](README.zh-Hant.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português (BR)](README.pt-BR.md)

> 完整中文文件請見 [../README.md](../README.md)。

## 概覽

OfficeAce Daily 會領取果辦（OfficeAce / OfficeClaw）帳號目前可用的獎勵。每日簽到與一次性新人禮由服務端同一個 claim 動作發放。腳本會在領取前讀取 subscription，並在服務回傳足夠資料時報告實際額度增量。重複領取會按冪等結果顯示今日無可領獎勵或已領過。

控制面請求使用華為雲臨時 AK/SK、`security_token` 與 `project_id`，現有文件記錄的壽命約 2 小時。閘道 Basic 憑據可以長期有效，但它用於模型轉發，單獨不足以完成簽到。

## 核心能力

- 一次 claim 領取當天可用獎勵與一次性新人禮。
- 為 `cn-southwest-2/apic` 區域作用域實作 V11-HMAC-SHA256。
- 先讀取訂閱基線，並在 claim 回執包含最新清單時按 `current_value` 計算增量。
- 使用 `OFFICEACE_TOKENS` 支援多帳號。
- 提供 `--query` 只讀核對額度。
- 單檔自包含，青龍只需上傳一個 Python 腳本。
- 可選企業微信與 PushPlus 推送。

## 憑據壽命

| 憑據 | 壽命 | 用途 | `officeace_get_token.py` 能否讀取 |
| :--- | :--- | :--- | :--- |
| 閘道 Basic `key:secret` | 不過期 | 模型轉發 | 可以 |
| 控制面 AK/SK + STS + `project_id` | 約 2 小時 | 額度查詢與簽到 | 不可 |

桌面端 `models.json` 可以提供閘道基址與 Basic 憑據。控制面臨時憑據需要透過客戶端或控制台流程另外取得，再注入環境變數。

## 讀取本機桌面端設定

```bash
python officeace_get_token.py
python officeace_get_token.py --list
python officeace_get_token.py --json
python officeace_get_token.py --path <檔案或目錄>
```

預設搜尋：

```text
~/.office-claw/.jiuwenclaw/config/routing_state/users/<帳號ID>/models.json
```

工具相容 `api_key` 內的 `key:secret`，也支援 `custom_headers` 中的 `Authorization: Basic ...`。

## 最短青龍設定

1. 上傳 `officeace_daily.py`。
2. 新增 `OFFICEACE_TOKENS`。
3. 建立定時任務：

```bash
task officeace_daily.py
```

建議 cron：

```cron
10 9 * * *
```

多帳號格式：

```text
備註|AK_VALUE|SK_VALUE|STS_VALUE|PROJECT_ID|https://modelgw-xxxx.cn-southwest-2.huaweicloud-agentarts.com/v2
副號|AK_VALUE|SK_VALUE|STS_VALUE|PROJECT_ID|https://modelgw-yyyy.cn-southwest-2.huaweicloud-agentarts.com/v2
```

也可以省略備註，使用五段格式。帳號之間用換行或 `&` 分隔。

## 最短 GitHub Actions 設定

在 **Settings → Secrets and variables → Actions** 新增：

| Secret | 必填 | 用途 |
| :--- | :---: | :--- |
| `OFFICEACE_TOKENS` | 是 | 臨時控制面憑據 |
| `QYWX_TOKEN` | 否 | 企業微信機器人 key |
| `PLUSPLUS_TOKEN` | 否 | PushPlus token |

內建工作流程預設只能手動觸發。先執行 **Actions → OfficeAce Daily → Run workflow**。要啟用排程時，取消註解：

```yaml
schedule:
  - cron: '10 1 * * *'
```

此 cron 使用 UTC，`10 1 * * *` 等於北京時間每天 09:10。控制面憑據約 2 小時失效，因此排程執行時 Secret 內必須仍為有效的臨時憑據。

## 關鍵環境變數

| 變數 | 必填 | 說明 |
| :--- | :---: | :--- |
| `OFFICEACE_TOKENS` | 多帳號 | 多帳號資料，每條五段或六段 |
| `OFFICEACE_AK` | 否 | 單帳號 Access Key |
| `OFFICEACE_SK` | 否 | 單帳號 Secret Key |
| `OFFICEACE_STS` | 否 | 單帳號 `security_token` |
| `OFFICEACE_PROJECT_ID` | 否 | 單帳號 project ID |
| `OFFICEACE_BASE_URL` | 否 | 單帳號閘道基址 |
| `OFFICEACE_CLIENT_DIR` | 否 | 本機憑據工具的搜尋根目錄 |
| `QYWX_TOKEN` | 否 | 企業微信機器人 key，也相容 `WECHAT_WEBHOOK` |
| `PLUSPLUS_TOKEN` | 否 | PushPlus token |
| `NO_NOTIFY` | 否 | 設為 `1` 時關閉推送 |

`OFFICEACE_TOKENS` 非空時優先於單帳號變數。

## 命令列參數

| 參數 | 作用 |
| :--- | :--- |
| 無 | 為全部帳號領取獎勵 |
| `--only N` | 只執行第 N 個帳號 |
| `--query` | 只查詢額度與活動狀態，不領取 |

關閉推送請設定 `NO_NOTIFY=1`。

## 驗證範圍

倉庫記錄了 6 個官方簽名向量逐位元組一致的結果，涵蓋 SDK / V11、轉義路徑、查詢排序與 V11 派生金鑰表示。離線檢查另涵蓋 `+50` 額度增量、冪等領取、臨時憑據過期、多帳號、脫敏與 GBK 主控台。

倉庫沒有提供真實帳號線上領取成功的證據。第一次實跑時，請先用 `--query` 核對憑據、基址與 subscription，再啟用領取排程。

## 隱私提醒

腳本不落盤控制面憑據，`officeace_get_token.py` 只讀取本機設定。日誌僅顯示 AK 遮罩片段。請勿在倉庫、Issue 或公開 Actions 輸出中貼出 `OFFICEACE_TOKENS`、STS、完整 `models.json` 或未脫敏日誌。

## 連結

- [Releases](https://github.com/L0NE-6/OfficeAce-Daily/releases)
- [Issues](https://github.com/L0NE-6/OfficeAce-Daily/issues)
- [簡體中文完整文件](../README.md)
- [更新記錄](../CHANGELOG.md)

## 免責聲明

本專案供個人學習與自動化使用。請遵守 OfficeAce、OfficeClaw、華為雲與相關服務條款，並自行承擔使用風險。
