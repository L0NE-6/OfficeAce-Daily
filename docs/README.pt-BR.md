# 🏢 OfficeAce Daily

**Coleta diária de recompensas do OfficeAce / OfficeClaw, com assinatura V11-HMAC-SHA256 e releitura da assinatura de quota.**

[简体中文](../README.md) | [English](README.en.md) | [繁體中文](README.zh-Hant.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português (BR)](README.pt-BR.md)

> A documentação chinesa completa está em [../README.md](../README.md).

## Visão geral

O OfficeAce Daily coleta as recompensas atualmente disponíveis para uma conta OfficeAce / OfficeClaw. O check-in diário e o benefício único de novo usuário são entregues pela mesma ação de claim no servidor. O script lê a subscription antes do claim e calcula o aumento real de quota a partir de `current_value` quando a resposta contém dados suficientes. Repetições são tratadas como resultado idempotente de "nada disponível hoje" ou "já recebido".

As requisições de control plane usam credenciais temporárias AK/SK do Huawei Cloud, security token e project ID. A documentação existente registra validade de cerca de duas horas. A credencial Basic do gateway pode durar muito mais, mas é usada para encaminhamento de modelos e não basta sozinha para o check-in.

## Recursos principais

- Coleta as recompensas diárias e de novo usuário em uma chamada de claim.
- Implementa V11-HMAC-SHA256 para o escopo `cn-southwest-2/apic`.
- Lê a subscription antes do claim e compara `current_value` na resposta do claim quando possível.
- Suporta várias contas com `OFFICEACE_TOKENS`.
- Oferece `--query` para verificar a quota em modo somente leitura.
- Executa como um único script Python autocontido.
- Envia notificações opcionais pelo WeCom e PushPlus.

## Validade das credenciais

| Credencial | Validade | Finalidade | Leitura pelo utilitário local |
| :--- | :--- | :--- | :--- |
| Gateway Basic `key:secret` | não expira | Encaminhamento de modelos | Sim |
| Control plane AK/SK + STS + `project_id` | cerca de 2 horas | Quota e check-in | Não |

O `models.json` do cliente desktop pode fornecer a URL do gateway e a credencial Basic. A credencial temporária do control plane deve ser obtida pelo cliente ou console e configurada separadamente.

## Leitura da configuração desktop local

```bash
python officeace_get_token.py
python officeace_get_token.py --list
python officeace_get_token.py --json
python officeace_get_token.py --path <arquivo-ou-diretório>
```

Por padrão, a ferramenta procura:

```text
~/.office-claw/.jiuwenclaw/config/routing_state/users/<account-id>/models.json
```

Ela aceita `api_key` com `key:secret` ou um cabeçalho `Authorization: Basic ...` em `custom_headers`.

## Configuração mínima no Qinglong

1. Envie `officeace_daily.py`.
2. Adicione `OFFICEACE_TOKENS`.
3. Crie a tarefa agendada:

```bash
task officeace_daily.py
```

Cron sugerido:

```cron
10 9 * * *
```

Formato com várias contas:

```text
observação|AK_VALUE|SK_VALUE|STS_VALUE|PROJECT_ID|https://modelgw-xxxx.cn-southwest-2.huaweicloud-agentarts.com/v2
segunda|AK_VALUE|SK_VALUE|STS_VALUE|PROJECT_ID|https://modelgw-yyyy.cn-southwest-2.huaweicloud-agentarts.com/v2
```

O formato de cinco campos sem observação também é aceito. Separe as contas por quebras de linha ou `&`.

## Configuração mínima no GitHub Actions

Adicione estes Secrets em **Settings → Secrets and variables → Actions**:

| Secret | Obrigatório | Finalidade |
| :--- | :---: | :--- |
| `OFFICEACE_TOKENS` | sim | Credenciais temporárias do control plane |
| `QYWX_TOKEN` | opcional | Chave do bot WeCom |
| `PLUSPLUS_TOKEN` | opcional | Token do PushPlus |

O workflow incluído é somente manual por padrão. Execute **Actions → OfficeAce Daily → Run workflow** para validar. Para habilitar a agenda, remova o comentário:

```yaml
schedule:
  - cron: '10 1 * * *'
```

O cron usa UTC. `10 1 * * *` corresponde a 09:10 no horário de Pequim. Como a credencial do control plane expira em cerca de duas horas, a execução agendada precisa ter uma credencial temporária válida no Secret.

## Variáveis de ambiente principais

| Variável | Obrigatória | Descrição |
| :--- | :---: | :--- |
| `OFFICEACE_TOKENS` | várias contas | Várias contas, com cinco ou seis campos por linha |
| `OFFICEACE_AK` | opcional | Access Key de uma conta |
| `OFFICEACE_SK` | opcional | Secret Key de uma conta |
| `OFFICEACE_STS` | opcional | Security token de uma conta |
| `OFFICEACE_PROJECT_ID` | opcional | Project ID de uma conta |
| `OFFICEACE_BASE_URL` | opcional | URL base do gateway para uma conta |
| `OFFICEACE_CLIENT_DIR` | opcional | Raiz de busca do leitor local de credenciais |
| `QYWX_TOKEN` | opcional | Chave do bot WeCom; `WECHAT_WEBHOOK` também é aceito |
| `PLUSPLUS_TOKEN` | opcional | Token do PushPlus |
| `NO_NOTIFY` | opcional | Defina `1` para desativar notificações |

Quando não está vazio, `OFFICEACE_TOKENS` tem precedência sobre as variáveis de conta única.

## Opções de linha de comando

| Opção | Efeito |
| :--- | :--- |
| nenhuma | Coleta recompensas de todas as contas |
| `--only N` | Executa somente a conta número N |
| `--query` | Consulta quota e atividade sem fazer claim |

Use `NO_NOTIFY=1` no ambiente para desativar notificações.

## Escopo de verificação

O repositório registra seis vetores oficiais de assinatura comparados byte a byte, incluindo SDK / V11, caminhos escapados, ordenação de query e representação da chave derivada V11. As verificações offline também cobrem incremento de `+50`, claim idempotente, expiração da credencial temporária, várias contas, mascaramento e console GBK.

O repositório não inclui evidência de uma coleta online bem-sucedida em conta real. Na primeira execução, use `--query` para verificar credencial, URL base e subscription antes de habilitar uma agenda de coleta.

## Privacidade

Os scripts não persistem credenciais do control plane. `officeace_get_token.py` apenas lê a configuração local. Os logs mostram o AK mascarado. Não publique `OFFICEACE_TOKENS`, STS, um `models.json` completo ou logs sem máscara em repositório, Issue ou saída pública do Actions.

## Limites de uso e redistribuição

O repositório oficial, os scripts, as instruções de implantação e as Releases permanecem gratuitos e públicos. Sem autorização escrita explícita do autor, não empacote este projeto como recurso pago, serviço de implantação paga ou serviço de atualização paga; não remova a atribuição para alegar autoria original; não se passe pelo autor; e não use a identidade, o nome, o avatar ou os QR codes de pagamento do autor para sugerir endosso oficial. Também não republique o projeto em contas, grupos, canais ou plataformas pagas sem relação com ele para ganhar seguidores, desviar tráfego ou revender. Em caso de violação, o autor pode solicitar a remoção e pode pausar atualizações, arquivar ou excluir o repositório. Consulte as regras completas em [NOTICE.md](../NOTICE.md).

## Links

- [Releases](https://github.com/L0NE-6/OfficeAce-Daily/releases)
- [Issues](https://github.com/L0NE-6/OfficeAce-Daily/issues)
- [README em chinês](../README.md)
- [Histórico de alterações](../CHANGELOG.md)

## Aviso

Este projeto é destinado a aprendizado pessoal e automação. Respeite os termos do OfficeAce, OfficeClaw, Huawei Cloud e serviços relacionados. O uso é por sua conta e risco.
