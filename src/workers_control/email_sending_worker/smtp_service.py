import email.utils
from contextlib import contextmanager
from dataclasses import dataclass
from email.message import EmailMessage
from smtplib import SMTP, SMTP_SSL
from typing import Generator

from workers_control.email_sending_worker.interface import EmailSenderPlugin


@dataclass
class SmtpMailServerConfig:
    mail_server: str
    mail_port: int
    encryption_type: str
    username: str | None = None
    password: str | None = None


@dataclass
class SmtpMailService(EmailSenderPlugin):
    config: SmtpMailServerConfig

    def send_message(
        self,
        subject: str,
        recipient: list[str],
        html: str,
        sender: str,
    ) -> None:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = sender
        message["Date"] = email.utils.formatdate(localtime=True)
        message.set_content(html, subtype="html")

        with self.create_smtp_connection() as connection:
            message["Message-ID"] = email.utils.make_msgid(domain="workers-control")
            message["To"] = recipient
            connection.send_message(message)

    @contextmanager
    def create_smtp_connection(self) -> Generator[SMTP | SMTP_SSL, None, None]:
        server = self.config.mail_server
        port = self.config.mail_port
        encryption_type = self.config.encryption_type
        connection: SMTP | SMTP_SSL

        if encryption_type == "ssl":
            connection = SMTP_SSL(server, port=port or 465)
        else:
            connection = SMTP(server, port=port or 587)
            connection.starttls()

        connection.ehlo()
        username = self.config.username
        password = self.config.password
        if username and password:
            connection.login(username, password)
        yield connection
        connection.quit()
