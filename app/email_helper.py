import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import logging

load_dotenv()
log = logging.getLogger("backup")

def enviar_email(assunto, corpo):
    try:
        msg = MIMEMultipart()
        msg["From"] = os.getenv("EMAIL_FROM")
        msg["To"] = os.getenv("EMAIL_TO")
        msg["Subject"] = assunto

        msg.attach(MIMEText(corpo, "plain"))

        with smtplib.SMTP(os.getenv("EMAIL_SMTP"), int(os.getenv("EMAIL_PORT"))) as server:
            server.starttls()
            server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASSWORD"))
            server.send_message(msg)

        log.info("✉️ E-mail enviado com sucesso.")
    except Exception as e:
        log.error(f"❌ Falha ao enviar e-mail: {e}")