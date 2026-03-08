import email.utils
from contextlib import contextmanager
from email.message import EmailMessage
from smtplib import SMTP, SMTP_SSL
from typing import Generator, Protocol


class MailService(Protocol):
    def send_message(
        self,
        subject: str,
        recipient: list,
        html: str,
        sender: str,
    ) -> None: ...


class SmtpMailService:
    def __init__(
        self,
        mail_server: str,
        mail_port: int,
        encryption_type: str,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        self.mail_server = mail_server
        self.mail_port = mail_port
        self.encryption_type = encryption_type
        self.username = username
        self.password = password

    def send_message(
        self,
        subject: str,
        recipient: list,
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
        server = self.mail_server
        port = self.mail_port
        encryption_type = self.encryption_type
        connection: SMTP | SMTP_SSL

        if encryption_type == "ssl":
            connection = SMTP_SSL(server, port=port or 465)
        else:
            connection = SMTP(server, port=port or 587)
            connection.starttls()

        connection.ehlo()
        username = self.username
        password = self.password
        if username and password:
            connection.login(username, password)
        yield connection
        connection.quit()
