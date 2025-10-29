from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
import os

load_dotenv()
SENDGRID_API_KEY = os.getenv("SENDGRID_KEY")

def enviar_email(destinatario, nome, assunto, corpo_html):
    mensagem = Mail(
        from_email="poisola7@gmail.com",
        to_emails=destinatario,
        subject=assunto,
        html_content=corpo_html  # agora envia HTML
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(mensagem)
        print("📧 Email enviado com sucesso via SendGrid.")
    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")
