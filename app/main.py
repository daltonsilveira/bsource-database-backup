import os
import subprocess
from datetime import datetime
import pytz
from dotenv import load_dotenv
from botocore.exceptions import ClientError, NoCredentialsError
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import sys
from email_helper import enviar_email
from db_dumper import create_dumper_from_env
from storage_provider import create_storage_from_env

# Carrega variáveis do .env
load_dotenv()

# ── Logging ──────────────────────────────────────────────────────────────────
# SEQ é opcional: só inicializa se SEQ_URL estiver definido
_seq_url = os.getenv("SEQ_URL")

if _seq_url:
    import seqlog

    seqlog.log_to_seq(
        server_url=_seq_url,
        api_key=os.getenv("SEQ_API_KEY", None),
        level=logging.INFO,
        batch_size=10,
        auto_flush_timeout=1,
        override_root_logger=True,
    )
    seqlog.set_global_log_properties(
        Application="BSource.DbBackup",
        Environment=os.getenv("APP_ENV", "Development"),
    )
else:
    logging.basicConfig(level=logging.INFO)

# Console handler (sempre ativo)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s"))

log = logging.getLogger("backup")
log.addHandler(console_handler)

# ── Timezone ─────────────────────────────────────────────────────────────────
TIMEZONE_NAME = os.getenv("TIMEZONE", "America/Sao_Paulo")
try:
    TIMEZONE = pytz.timezone(TIMEZONE_NAME)
except pytz.UnknownTimeZoneError:
    log.warning(f"⚠️ Timezone '{TIMEZONE_NAME}' não reconhecido, usando 'America/Sao_Paulo'")
    TIMEZONE = pytz.timezone("America/Sao_Paulo")

# ── Database dumper ──────────────────────────────────────────────────────────
try:
    dumper = create_dumper_from_env()
    DB_DATABASE = os.getenv("DB_DATABASE")
    DB_TYPE = os.getenv("DB_TYPE", "").lower().strip()
    log.info(f"✅ Dumper configurado: {DB_TYPE}")
except ValueError as e:
    log.error(f"❌ Erro na configuração do banco de dados: {e}")
    dumper = None
    DB_DATABASE = None
    DB_TYPE = None

# ── Storage provider ────────────────────────────────────────────────────────
try:
    storage = create_storage_from_env()
    STORAGE_TYPE = os.getenv("STORAGE_TYPE", "").lower().strip()
    log.info(f"✅ Storage configurado: {STORAGE_TYPE}")
except ValueError as e:
    log.error(f"❌ Erro na configuração do storage: {e}")
    storage = None
    STORAGE_TYPE = None


def get_local_datetime():
    """Retorna datetime atual no fuso horário configurado."""
    return datetime.now(TIMEZONE)


def gerar_backup():
    log.info("🔄 Iniciando backup...")

    if dumper is None:
        log.error("❌ Dumper não configurado. Backup cancelado.")
        return

    if storage is None:
        log.error("❌ Storage não configurado. Backup cancelado.")
        return

    local_time = get_local_datetime()
    timestamp = local_time.strftime("%Y%m%d_%H%M%S")
    extension = dumper.get_file_extension()
    backup_filename = f"backup_{DB_DATABASE}_{timestamp}{extension}"
    backup_filepath = f"/tmp/{backup_filename}"

    try:
        # Executa o dump via abstração
        dumper.dump(backup_filepath)
        log.info(f"✅ Backup gerado: {backup_filepath}")

        # Metadados para o arquivo
        metadata = dumper.get_metadata()
        metadata.update({
            "upload-timestamp": local_time.isoformat(),
            "timezone": TIMEZONE_NAME,
        })

        # Upload para o storage
        remote_path = storage.upload_file(backup_filepath, backup_filename, metadata)
        log.info(f"✅ Backup enviado para {STORAGE_TYPE}: {remote_path}")

        data_hora_br = local_time.strftime("%d/%m/%Y às %H:%M:%S")
        enviar_email(
            "Database Backup - SUCESSO",
            f"Backup '{backup_filename}' da base de dados '{DB_DATABASE}' ({DB_TYPE}) "
            f"realizado com sucesso em {data_hora_br} ({TIMEZONE_NAME})!",
        )

    except subprocess.CalledProcessError as e:
        log.error(f"❌ Erro ao gerar backup: {e}")
        data_hora_br = get_local_datetime().strftime("%d/%m/%Y às %H:%M:%S")
        enviar_email(
            "Database Backup - ERRO",
            f"Falha ao gerar o backup da base de dados '{DB_DATABASE}' ({DB_TYPE}) "
            f"em {data_hora_br} ({TIMEZONE_NAME}).\n\nErro: {e}",
        )

    except (ClientError, NoCredentialsError, Exception) as e:
        log.error(f"❌ Erro no upload para {STORAGE_TYPE}: {e}")
        data_hora_br = get_local_datetime().strftime("%d/%m/%Y às %H:%M:%S")
        enviar_email(
            "Database Backup - ERRO",
            f"Falha no upload do backup da base de dados '{DB_DATABASE}' ({DB_TYPE}) "
            f"em {data_hora_br} ({TIMEZONE_NAME}).\n\nErro: {e}",
        )

    finally:
        if os.path.exists(backup_filepath):
            os.remove(backup_filepath)
            log.info("🗑️ Arquivo de backup local removido.")


def main():
    gerar_backup()


if __name__ == "__main__":
    CRON_SCHEDULE = os.getenv("CRON_SCHEDULE", "0 */12 * * *")
    log.info(f"📅 Backup agendado com cron: {CRON_SCHEDULE}")

    scheduler = BlockingScheduler()
    trigger = CronTrigger.from_crontab(CRON_SCHEDULE)
    scheduler.add_job(main, trigger)

    main()  # executa imediatamente
    scheduler.start()