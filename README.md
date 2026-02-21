# BSource Database Backup

Sistema automatizado de backup de bases de dados com suporte a múltiplos engines e storage providers, notificações por email e logging estruturado.

## 🚀 Funcionalidades

- ✅ Backup automatizado de bases de dados **PostgreSQL**, **MySQL**, **MariaDB** e **SQL Server**
- ☁️ Upload automático para **Cloudflare R2** ou **AWS S3**
- 📧 Notificações por email de sucesso/erro
- 📊 Logging estruturado com integração SEQ (opcional)
- ⏰ Agendamento flexível via CRON
- 🐳 Containerizado com Docker

## 🛠️ Configuração

### 1. Pré-requisitos

- Python 3.9+
- Docker (opcional)
- Cliente do banco de dados correspondente ao `DB_TYPE` configurado:
  - PostgreSQL: `pg_dump`
  - MySQL/MariaDB: `mysqldump`
  - SQL Server: `sqlcmd`
- Conta no Cloudflare R2 ou AWS S3

### 2. Configuração do Storage

#### Cloudflare R2

1. Acesse o painel do Cloudflare > R2 Object Storage
2. Crie um bucket para os backups
3. Em "Manage R2 API tokens", crie um token com permissões Object Read & Write
4. Anote o Endpoint URL, Access Key ID e Secret Access Key
5. Configure `STORAGE_TYPE=r2` no `.env`

#### AWS S3

1. Crie um bucket S3 na região desejada
2. Crie um IAM user com permissões `s3:PutObject` e `s3:ListBucket`
3. Anote Access Key ID e Secret Access Key
4. Configure `STORAGE_TYPE=s3` e `STORAGE_REGION` no `.env`

### 3. Variáveis de ambiente

Copie o arquivo `.env.example` para `.env` e configure:

```bash
cp .env.example .env
```

### 4. Instalação

#### Usando Python (desenvolvimento):
```bash
cd app
pip install -r requirements.txt
python main.py
```

#### Usando Docker (produção):
```bash
docker-compose up -d
```

## 📋 Configurações disponíveis

### Base de Dados

| Variável | Descrição | Padrão | Obrigatória |
|----------|-----------|--------|-------------|
| `DB_TYPE` | Tipo de base de dados (`postgres`, `mysql`, `mariadb`, `mssql`) | - | ✅ |
| `DB_HOST` | Host da base de dados | - | ✅ |
| `DB_PORT` | Porta da base de dados | - | ✅ |
| `DB_USER` | Usuário da base de dados | - | ✅ |
| `DB_PASSWORD` | Senha da base de dados | - | ✅ |
| `DB_DATABASE` | Nome da base de dados | - | ✅ |

### Storage

| Variável | Descrição | Padrão | Obrigatória |
|----------|-----------|--------|-------------|
| `STORAGE_TYPE` | Tipo de storage (`r2`, `s3`) | - | ✅ |
| `STORAGE_ENDPOINT_URL` | URL do endpoint | - | ✅ (R2) / ❌ (S3) |
| `STORAGE_ACCESS_KEY_ID` | Access Key do storage | - | ✅ |
| `STORAGE_SECRET_ACCESS_KEY` | Secret Key do storage | - | ✅ |
| `STORAGE_BUCKET_NAME` | Nome do bucket | - | ✅ |
| `STORAGE_DESTINATION_FOLDER` | Pasta destino no bucket | `backups/` | ❌ |
| `STORAGE_REGION` | Região AWS | - | ✅ (S3) / ❌ (R2) |

### Agendamento e Geral

| Variável | Descrição | Padrão | Obrigatória |
|----------|-----------|--------|-------------|
| `CRON_SCHEDULE` | Agendamento CRON | `0 */12 * * *` | ❌ |
| `TIMEZONE` | Fuso horário para logs e backups | `America/Sao_Paulo` | ❌ |
| `APP_ENV` | Ambiente da aplicação | `Development` | ❌ |

### Email

| Variável | Descrição | Padrão | Obrigatória |
|----------|-----------|--------|-------------|
| `EMAIL_FROM` | Remetente do email | - | ✅ |
| `EMAIL_TO` | Destinatário do email | - | ✅ |
| `EMAIL_SMTP` | Servidor SMTP | - | ✅ |
| `EMAIL_PORT` | Porta SMTP | - | ✅ |
| `EMAIL_USER` | Usuário SMTP | - | ✅ |
| `EMAIL_PASSWORD` | Senha SMTP | - | ✅ |

### Logging (SEQ — opcional)

| Variável | Descrição | Padrão | Obrigatória |
|----------|-----------|--------|-------------|
| `SEQ_URL` | URL do servidor SEQ | - | ❌ |
| `SEQ_API_KEY` | API Key do SEQ | - | ❌ |

> **Nota:** Se `SEQ_URL` não estiver definido, apenas logging para console será utilizado.

## 🔧 Desenvolvimento

### Estrutura do projeto:
```
├── app/
│   ├── __init__.py              # Pacote Python
│   ├── main.py                  # Aplicação principal
│   ├── db_dumper.py             # Abstração de dump de bases de dados
│   ├── storage_provider.py      # Abstração de storage providers
│   ├── email_helper.py          # Auxiliar para emails
│   ├── requirements.txt         # Dependências Python
│   └── backups/                 # Backups locais temporários
├── docker/
│   ├── docker-compose.yaml      # Configuração Docker
│   └── Dockerfile               # Imagem Docker
├── .env.example                 # Exemplo de configuração
└── .gitignore                   # Arquivos ignorados pelo Git
```

### Arquitetura:

```
                    ┌───────────────────┐
                    │      main.py      │  (scheduler + orquestração)
                    └─────┬───────┬─────┘
                          │       │
              ┌───────────┘       └───────────┐
              ▼                               ▼
   ┌─────────────────┐              ┌─────────────────┐
   │  DatabaseDumper  │ (ABC)       │ StorageProvider  │ (ABC)
   ├─────────────────┤              ├─────────────────┤
   │ PostgresDumper   │              │ R2Storage        │
   │ MySQLDumper      │              │ S3Storage        │
   │ MSSQLDumper      │              └─────────────────┘
   └─────────────────┘
```

### Bases de dados suportadas:

| DB_TYPE | Engine | Ferramenta CLI | Extensão |
|---------|--------|---------------|----------|
| `postgres` | PostgreSQL | `pg_dump` | `.sql` |
| `mysql` | MySQL | `mysqldump` | `.sql` |
| `mariadb` | MariaDB | `mysqldump` | `.sql` |
| `mssql` | SQL Server | `sqlcmd` | `.bak` |

## 🕐 Configuração de Fuso Horário

O sistema suporta configuração de fuso horário através da variável `TIMEZONE`. Por padrão, usa o horário de São Paulo.

### Exemplos de timezones suportados:
- `America/Sao_Paulo` - Horário de Brasília (padrão)
- `America/New_York` - Horário de Nova York
- `Europe/London` - Horário de Londres
- `UTC` - Horário Universal Coordenado

### Comportamento:
- **Nomes dos backups**: Incluem timestamp no timezone configurado
- **Organização de pastas**: Agrupadas por data local (YYYYMMDD)
- **Emails de notificação**: Mostram horário local formatado
- **Logs**: Registram eventos no horário local
- **Metadados**: Incluem timezone para auditoria

## 📊 Monitoramento

- Logs estruturados enviados para SEQ (opcional — apenas se `SEQ_URL` for configurado)
- Logs no console sempre ativos
- Notificações por email para sucesso/erro com horário local
- Metadata nos arquivos de backup para auditoria

## ⚠️ Migração da v2.x para v3.0

A versão 3.0 introduz **breaking changes** nas variáveis de ambiente:

| v2.x | v3.0 |
|------|------|
| `PG_HOST` | `DB_HOST` |
| `PG_PORT` | `DB_PORT` |
| `PG_USER` | `DB_USER` |
| `PG_PASSWORD` | `DB_PASSWORD` |
| `PG_DATABASE` | `DB_DATABASE` |
| — | `DB_TYPE` (novo) |
| `R2_ENDPOINT_URL` | `STORAGE_ENDPOINT_URL` |
| `R2_ACCESS_KEY_ID` | `STORAGE_ACCESS_KEY_ID` |
| `R2_SECRET_ACCESS_KEY` | `STORAGE_SECRET_ACCESS_KEY` |
| `R2_BUCKET_NAME` | `STORAGE_BUCKET_NAME` |
| `R2_DESTINATION_FOLDER` | `STORAGE_DESTINATION_FOLDER` |
| — | `STORAGE_TYPE` (novo) |
| — | `STORAGE_REGION` (novo, S3 apenas) |

> As variáveis antigas (`PG_*`, `R2_*`) **não funcionam mais**. Atualize o seu `.env` conforme o `.env.example`.

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.