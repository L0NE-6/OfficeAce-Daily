# 🏢 OfficeAce Daily

**OfficeAce / OfficeClaw のデイリー報酬取得ツールです。V11-HMAC-SHA256 署名とサブスクリプション再読取を内蔵しています。**

[简体中文](../README.md) | [English](README.en.md) | [繁體中文](README.zh-Hant.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português (BR)](README.pt-BR.md)

> 完全な中国語ドキュメントは [../README.md](../README.md) にあります。

## 概要

OfficeAce Daily は、OfficeAce / OfficeClaw アカウントで現在受け取れる報酬を取得します。デイリーチェックインと一度限りの新規ユーザー特典は、サーバー側の同じ claim アクションで配布されます。スクリプトは claim 前に subscription を読み取り、claim 応答に十分なデータが含まれる場合は `current_value` から実際のクォータ増加を報告します。再実行時は冪等な「本日分なし」または「受取済み」として扱います。

コントロールプレーンのリクエストには Huawei Cloud の一時 AK/SK、security token、project ID を使用します。既存文書では有効期間は約 2 時間です。ゲートウェイの Basic 認証情報は長期間有効ですが、モデル転送用であり、単独ではチェックインに足りません。

## 主な機能

- 1 回の claim で当日分と新規ユーザー特典を取得します。
- `cn-southwest-2/apic` スコープ向け V11-HMAC-SHA256 を実装します。
- claim 前の subscription を基準に、claim 応答の `current_value` から実際の増分を計算します。
- `OFFICEACE_TOKENS` で複数アカウントを扱えます。
- `--query` で読み取り専用のクォータ確認ができます。
- 単一の自己完結 Python スクリプトとして動作します。
- WeCom と PushPlus への任意通知に対応します。

## 認証情報の有効期間

| 認証情報 | 有効期間 | 用途 | ローカル読取ツール |
| :--- | :--- | :--- | :--- |
| ゲートウェイ Basic `key:secret` | 失効しない | モデル転送 | 読取可能 |
| コントロールプレーン AK/SK + STS + `project_id` | 約 2 時間 | クォータとチェックイン | 読取不可 |

デスクトップの `models.json` からゲートウェイ URL と Basic 認証情報を取得できます。一時的なコントロールプレーン認証情報は、クライアントまたはコンソールのフローから別途取得して環境変数へ設定します。

## ローカル設定の読み取り

```bash
python officeace_get_token.py
python officeace_get_token.py --list
python officeace_get_token.py --json
python officeace_get_token.py --path <ファイルまたはディレクトリ>
```

既定の検索先:

```text
~/.office-claw/.jiuwenclaw/config/routing_state/users/<account-id>/models.json
```

`api_key` に `key:secret` を格納する形式と、`custom_headers` の `Authorization: Basic ...` の両方に対応します。

## 最小構成の Qinglong

1. `officeace_daily.py` をアップロードします。
2. `OFFICEACE_TOKENS` を追加します。
3. 定期タスクを作成します。

```bash
task officeace_daily.py
```

推奨 cron:

```cron
10 9 * * *
```

複数アカウント形式:

```text
メモ|AK_VALUE|SK_VALUE|STS_VALUE|PROJECT_ID|https://modelgw-xxxx.cn-southwest-2.huaweicloud-agentarts.com/v2
second|AK_VALUE|SK_VALUE|STS_VALUE|PROJECT_ID|https://modelgw-yyyy.cn-southwest-2.huaweicloud-agentarts.com/v2
```

メモを省略した 5 フィールド形式も使用できます。アカウント間は改行または `&` で区切ります。

## 最小構成の GitHub Actions

**Settings → Secrets and variables → Actions** に次の Secrets を追加します。

| Secret | 必須 | 用途 |
| :--- | :---: | :--- |
| `OFFICEACE_TOKENS` | はい | 一時的なコントロールプレーン認証情報 |
| `QYWX_TOKEN` | 任意 | WeCom ボット key |
| `PLUSPLUS_TOKEN` | 任意 | PushPlus token |

同梱ワークフローは既定では手動実行のみです。**Actions → OfficeAce Daily → Run workflow** で検証します。スケジュールを有効にする場合は次をコメント解除します。

```yaml
schedule:
  - cron: '10 1 * * *'
```

UTC 表記の `10 1 * * *` は北京時間の毎日 09:10 です。コントロールプレーン認証情報は約 2 時間で失効するため、実行時点で Secret に有効な一時認証情報が必要です。

## 主要な環境変数

| 変数 | 必須 | 説明 |
| :--- | :---: | :--- |
| `OFFICEACE_TOKENS` | 複数アカウント | 1 行 5 または 6 フィールドの複数アカウント |
| `OFFICEACE_AK` | 任意 | 単一アカウントの Access Key |
| `OFFICEACE_SK` | 任意 | 単一アカウントの Secret Key |
| `OFFICEACE_STS` | 任意 | 単一アカウントの security token |
| `OFFICEACE_PROJECT_ID` | 任意 | 単一アカウントの project ID |
| `OFFICEACE_BASE_URL` | 任意 | 単一アカウントのゲートウェイ URL |
| `OFFICEACE_CLIENT_DIR` | 任意 | ローカル認証情報検索のルート |
| `QYWX_TOKEN` | 任意 | WeCom ボット key。`WECHAT_WEBHOOK` も使用可 |
| `PLUSPLUS_TOKEN` | 任意 | PushPlus token |
| `NO_NOTIFY` | 任意 | `1` で通知を無効化 |

`OFFICEACE_TOKENS` が空でない場合は、単一アカウント変数より優先されます。

## コマンドライン

| オプション | 動作 |
| :--- | :--- |
| なし | 全アカウントで報酬を取得 |
| `--only N` | N 番目のアカウントのみ実行 |
| `--query` | 取得せず、クォータと活動状態だけを確認 |

通知を無効にするには `NO_NOTIFY=1` を設定します。

## 検証範囲

リポジトリには、SDK / V11、エスケープされたパス、クエリ順序、V11 派生キー表現を含む 6 個の公式署名ベクトルのバイト単位一致が記録されています。オフライン確認では `+50` のクォータ増分、冪等 claim、一時認証情報の失効、複数アカウント、マスク、GBK コンソールも対象です。

実アカウントによるオンライン取得成功の証拠は含まれていません。初回の実運用では `--query` で認証情報、ベース URL、subscription を確認してから、取得スケジュールを有効にしてください。

## プライバシー

スクリプトはコントロールプレーン認証情報を保存しません。`officeace_get_token.py` はローカル設定を読むだけです。ログの AK はマスクされます。`OFFICEACE_TOKENS`、STS、完全な `models.json`、未マスクのログをリポジトリ、Issue、公開 Actions 出力へ掲載しないでください。

## リンク

- [Releases](https://github.com/L0NE-6/OfficeAce-Daily/releases)
- [Issues](https://github.com/L0NE-6/OfficeAce-Daily/issues)
- [中国語 README](../README.md)
- [変更履歴](../CHANGELOG.md)

## 免責事項

本プロジェクトは個人の学習と自動化を目的としています。OfficeAce、OfficeClaw、Huawei Cloud および関連サービスの利用規約を確認し、自己責任で使用してください。
