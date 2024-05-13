from smtplib import SMTP_SSL
from ssl import create_default_context
from email.message import EmailMessage


def send_email(
        subject: str,
        message: str,
        email_from: str,
        email_to: str,
        password: str
):
    context = create_default_context()

    msg = EmailMessage()
    msg.set_content(message)

    msg['Subject'] = subject
    msg['From'] = email_from
    msg['To'] = email_to

    with SMTP_SSL(host='smtp.rambler.ru', port=465, context=context) as server:
        server.login(email_to, password=password)
        server.send_message(msg)
