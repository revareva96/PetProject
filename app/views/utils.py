import smtplib
import ssl
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from threading import Thread

from app.config.config import get_settings

settings = get_settings()

register_head = """
    Подтверждение регистрации
"""

recover_head = """
    Восстановление пароля
"""


def create_message_confirm_str(uid: uuid.UUID) -> str:
    return f""""
        <html>
            <body>
                <h1>
                    Подтверждение регистрации.
                </h1>
                Добрый день, для подтверждения регистрации перейдите по 
                <a href='http://localhost:3001/confirm?confirm={uid}' style='text-decoration: none'>ссылке</a>.<br>
                <br>
                Отвечать на данное сообщение не надо.<br>
                Если Вы не регестрировались, то просьба проигнорировать сообщение и связаться с нами.<br>
                <br>
                <b>С уважением, служба поддержки</b>        
            </body>
        </html>
    """


def create_message_recover_str(uid: uuid.UUID) -> str:
    return f""""
        <html>
            <body>
                <h1>
                    Восстановление пароля.
                </h1>
                Добрый день, для восстановления пароля перейдите по 
                <a href='http://localhost:3001/recover?recover={uid}' style='text-decoration: none'>ссылке</a>.<br>
                <br>
                Отвечать на данное сообщение не надо.<br>
                Если Вы не запрашивали восстановление пароля, 
                то просьба проигнорировать сообщение и связаться с нами.<br>
                <br>
                <b>С уважением, служба поддержки</b>        
            </body>
        </html>
    """


messages = {
    'confirm': create_message_confirm_str,
    'recover': create_message_recover_str,
}

heads = {
    'confirm': register_head,
    'recover': recover_head,
}


def create_message(email: str, typ: str, uid: uuid.UUID) -> str:
    message = MIMEMultipart("alternative")
    message['From'] = settings.smtp_from
    message['To'] = email
    message['Subject'] = 'Cigar for soul'

    plain_text_message = MIMEText(heads[typ], 'plain', 'utf-8')
    html_message = MIMEText(
        messages[typ](uid), 'html', 'utf-8',
    )
    message.attach(plain_text_message)
    message.attach(html_message)
    return message.as_string()


def send_message(email: str, typ: str, uid: uuid.UUID) -> None:
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(
            settings.smtp_host,
            settings.smtp_port,
            context=context,
    ) as server:
        server.login(settings.smtp_user, settings.smtp_password)
        server.sendmail(
            settings.smtp_from, email, create_message(email, typ, uid),
        )


def send_message_in_thread(email: str, typ: str, uid: uuid.UUID) -> None:
    thread = Thread(
        target=send_message, kwargs={
            'email': email,
            'typ': typ,
            'uid': uid,
        },
    )
    thread.start()
