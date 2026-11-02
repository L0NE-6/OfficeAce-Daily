# 🏢 OfficeAce Daily

**OfficeAce / OfficeClaw의 일일 보상을 수집하며 V11-HMAC-SHA256 서명과 구독 재조회를 내장한 도구입니다.**

[简体中文](../README.md) | [English](README.en.md) | [繁體中文](README.zh-Hant.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português (BR)](README.pt-BR.md)

> 전체 중국어 문서는 [../README.md](../README.md)에서 확인할 수 있습니다.

## 개요

OfficeAce Daily는 OfficeAce / OfficeClaw 계정에서 현재 받을 수 있는 보상을 수령합니다. 일일 체크인과 일회성 신규 사용자 혜택은 서버의 동일한 claim 동작으로 지급됩니다. 스크립트는 claim 전에 subscription을 읽고 claim 응답에 충분한 데이터가 있으면 `current_value`에서 실제 quota 증가량을 계산합니다. 반복 실행은 멱등적인 "오늘 받을 항목 없음" 또는 "이미 수령" 결과로 처리합니다.

제어 평면 요청에는 Huawei Cloud 임시 AK/SK, security token, project ID를 사용합니다. 기존 문서에 기록된 유효 기간은 약 2시간입니다. 게이트웨이 Basic 자격 증명은 오래 유지될 수 있지만 모델 전달용이며 단독으로는 체크인에 충분하지 않습니다.

## 핵심 기능

- 한 번의 claim으로 당일 보상과 신규 사용자 혜택을 받습니다.
- `cn-southwest-2/apic` 범위의 V11-HMAC-SHA256을 구현합니다.
- claim 전 subscription을 기준으로 claim 응답의 `current_value`에서 실제 증가량을 계산합니다.
- `OFFICEACE_TOKENS`로 여러 계정을 지원합니다.
- `--query`로 읽기 전용 quota 확인을 제공합니다.
- 단일 자체 포함 Python 스크립트로 실행됩니다.
- 선택적으로 WeCom 및 PushPlus 알림을 보냅니다.

## 자격 증명 수명

| 자격 증명 | 수명 | 용도 | 로컬 추출 도구 |
| :--- | :--- | :--- | :--- |
| 게이트웨이 Basic `key:secret` | 만료되지 않음 | 모델 전달 | 읽기 가능 |
| 제어 평면 AK/SK + STS + `project_id` | 약 2시간 | Quota와 체크인 | 읽기 불가 |

데스크톱 `models.json`에서 게이트웨이 URL과 Basic 자격 증명을 얻을 수 있습니다. 임시 제어 평면 자격 증명은 클라이언트 또는 콘솔 흐름에서 별도로 얻어 환경 변수에 넣어야 합니다.

## 로컬 데스크톱 설정 읽기

```bash
python officeace_get_token.py
python officeace_get_token.py --list
python officeace_get_token.py --json
python officeace_get_token.py --path <파일-또는-디렉터리>
```

기본 검색 경로:

```text
~/.office-claw/.jiuwenclaw/config/routing_state/users/<account-id>/models.json
```

`api_key`에 `key:secret`을 넣는 형식과 `custom_headers`의 `Authorization: Basic ...`을 모두 지원합니다.

## 최소 Qinglong 설정

1. `officeace_daily.py`를 업로드합니다.
2. `OFFICEACE_TOKENS`를 추가합니다.
3. 예약 작업을 만듭니다.

```bash
task officeace_daily.py
```

권장 cron:

```cron
10 9 * * *
```

멀티 계정 형식:

```text
메모|AK_VALUE|SK_VALUE|STS_VALUE|PROJECT_ID|https://modelgw-xxxx.cn-southwest-2.huaweicloud-agentarts.com/v2
second|AK_VALUE|SK_VALUE|STS_VALUE|PROJECT_ID|https://modelgw-yyyy.cn-southwest-2.huaweicloud-agentarts.com/v2
```

메모를 생략한 5필드 형식도 지원합니다. 계정은 줄바꿈 또는 `&`로 구분합니다.

## 최소 GitHub Actions 설정

**Settings → Secrets and variables → Actions**에 다음 Secrets를 추가합니다.

| Secret | 필수 | 용도 |
| :--- | :---: | :--- |
| `OFFICEACE_TOKENS` | 예 | 임시 제어 평면 자격 증명 |
| `QYWX_TOKEN` | 선택 | WeCom 봇 key |
| `PLUSPLUS_TOKEN` | 선택 | PushPlus token |

포함된 워크플로는 기본적으로 수동 실행만 지원합니다. **Actions → OfficeAce Daily → Run workflow**로 검증합니다. 예약 실행을 켜려면 다음 주석을 해제합니다.

```yaml
schedule:
  - cron: '10 1 * * *'
```

UTC 기준 `10 1 * * *`는 베이징 시간 매일 09:10입니다. 제어 평면 자격 증명이 약 2시간 후 만료되므로 실행 시점에 Secret에 유효한 임시 자격 증명이 있어야 합니다.

## 주요 환경 변수

| 변수 | 필수 | 설명 |
| :--- | :---: | :--- |
| `OFFICEACE_TOKENS` | 멀티 계정 | 한 줄에 5개 또는 6개 필드를 쓰는 멀티 계정 |
| `OFFICEACE_AK` | 선택 | 단일 계정 Access Key |
| `OFFICEACE_SK` | 선택 | 단일 계정 Secret Key |
| `OFFICEACE_STS` | 선택 | 단일 계정 security token |
| `OFFICEACE_PROJECT_ID` | 선택 | 단일 계정 project ID |
| `OFFICEACE_BASE_URL` | 선택 | 단일 계정 게이트웨이 기본 URL |
| `OFFICEACE_CLIENT_DIR` | 선택 | 로컬 자격 증명 검색 루트 |
| `QYWX_TOKEN` | 선택 | WeCom 봇 key이며 `WECHAT_WEBHOOK`도 지원 |
| `PLUSPLUS_TOKEN` | 선택 | PushPlus token |
| `NO_NOTIFY` | 선택 | `1`로 설정하면 알림 비활성화 |

`OFFICEACE_TOKENS`가 비어 있지 않으면 단일 계정 변수보다 우선합니다.

## 명령행 옵션

| 옵션 | 동작 |
| :--- | :--- |
| 없음 | 모든 계정에서 보상 수령 |
| `--only N` | N번째 계정만 실행 |
| `--query` | 수령하지 않고 quota와 활동 상태만 확인 |

알림을 끄려면 `NO_NOTIFY=1`을 설정합니다.

## 검증 범위

저장소에는 SDK / V11, 이스케이프 경로, 쿼리 정렬, V11 파생 키 표현을 포함한 6개 공식 서명 벡터의 바이트 단위 일치가 기록되어 있습니다. 오프라인 검증은 `+50` quota 증가, 멱등 claim, 임시 자격 증명 만료, 멀티 계정, 마스킹, GBK 콘솔도 다룹니다.

실제 계정의 온라인 수령 성공 증거는 포함되어 있지 않습니다. 첫 실사용에서는 `--query`로 자격 증명, 기본 URL, subscription을 확인한 뒤 수령 일정을 활성화하세요.

## 개인정보 보호

스크립트는 제어 평면 자격 증명을 저장하지 않습니다. `officeace_get_token.py`는 로컬 설정만 읽습니다. 로그의 AK는 마스킹됩니다. `OFFICEACE_TOKENS`, STS, 전체 `models.json`, 마스킹되지 않은 로그를 저장소, Issue, 공개 Actions 출력에 게시하지 마세요.

## 링크

- [Releases](https://github.com/L0NE-6/OfficeAce-Daily/releases)
- [Issues](https://github.com/L0NE-6/OfficeAce-Daily/issues)
- [중국어 README](../README.md)
- [변경 기록](../CHANGELOG.md)

## 면책 조항

이 프로젝트는 개인 학습과 자동화를 위한 것입니다. OfficeAce, OfficeClaw, Huawei Cloud 및 관련 서비스 약관을 확인하고 사용 위험은 사용자 본인이 부담하세요.
