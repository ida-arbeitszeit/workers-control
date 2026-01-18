import email.utils
from contextlib import contextmanager
from email.message import EmailMessage
from smtplib import SMTP, SMTP_SSL
from typing import Generator

from flask import current_app

from .interface import EmailPlugin


class SmtpMailService(EmailPlugin):
    def send_message(
        self,
        subject: str,
        recipients: list[str],
        html: str,
        sender: str,
    ) -> None:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = sender
        message["Date"] = email.utils.formatdate(localtime=True)
        message.set_content(html, subtype="html")

        with self.create_smtp_connection() as connection:
            for recipient in recipients:
                del message["Message-ID"]
                del message["To"]
                message["Message-ID"] = email.utils.make_msgid(domain="workers-control")
                message["To"] = recipient
                connection.send_message(message)

    @classmethod
    @contextmanager
    def create_smtp_connection(cls) -> Generator[SMTP | SMTP_SSL, None, None]:
        server = current_app.config.get("MAIL_SERVER", "localhost")
        port = current_app.config.get("MAIL_PORT", 587)
        encryption_type = current_app.config.get("MAIL_ENCRYPTION_TYPE", "tls")
        connection: SMTP | SMTP_SSL

        if encryption_type == "ssl":
            connection = SMTP_SSL(server, port=port or 465)
        else:
            connection = SMTP(server, port=port or 587)
            connection.starttls()

        connection.ehlo()
        username = current_app.config.get("MAIL_USERNAME", "")
        password = current_app.config.get("MAIL_PASSWORD", "")
        if username and password:
            connection.login(username, password)
        yield connection
        connection.quit()
