"""
Módulo de envio de emails via SendGrid.

Este módulo:
- Carrega a chave da API SendGrid a partir das variáveis de ambiente.
- Expõe a função :func:`enviar_email` para envio de emails em formato HTML.

Requer:
    - Variável de ambiente ``SENDGRID_KEY`` definida no ficheiro ``.env``.
    - Conta SendGrid configurada e autorizada a enviar emails a partir
      do endereço definido em ``from_email``.
"""

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
import os

load_dotenv()
SENDGRID_API_KEY = os.getenv("SENDGRID_KEY")
"""str | None: Chave da API SendGrid lida da variável de ambiente
``SENDGRID_KEY``. Se estiver ausente, o envio de email irá falhar."""


def enviar_email(destinatario, nome, assunto, corpo_html):
    """Envia um email em formato HTML usando o serviço SendGrid.

    Args:
        destinatario (str): Endereço de email do destinatário.
        nome (str): Nome do destinatário (atualmente não utilizado
            no conteúdo, mas útil para personalização futura).
        assunto (str): Assunto do email.
        corpo_html (str): Conteúdo do email em HTML.

    Side Effects:
        - Envia uma mensagem via API SendGrid.
        - Escreve no terminal uma mensagem de sucesso ou de erro.

    Nota:
        Esta função assume que a variável de ambiente ``SENDGRID_KEY``
        está correctamente definida. Caso contrário, a criação do
        cliente SendGrid ou o envio da mensagem irá falhar e a exceção
        será impressa no terminal.

    """
    mensagem = Mail(
        from_email="poisola7@gmail.com",
        to_emails=destinatario,
        subject=assunto,
        html_content=corpo_html,  # envia HTML
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(mensagem)
        print("📧 Email enviado com sucesso via SendGrid.")
    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")
