from dataclasses import dataclass

from workers_control.core.datetime_service import DatetimeService
from workers_control.core.repositories import DatabaseGateway
from workers_control.flask.mail_service.interface import EmailPlugin


@dataclass
class DebugMailService(EmailPlugin):
    database_gateway: DatabaseGateway
    datetime_service: DatetimeService

    def send_message(
        self,
        subject: str,
        recipients: list[str],
        html: str,
        sender: str,
    ) -> None:
        for recipient in recipients:
            self.database_gateway.create_email(
                created_at=self.datetime_service.now(),
                recipient=recipient,
                sender=sender,
                subject=subject,
                html=html,
            )
            print("Email stored in outbox for sending:")
            print(f"recipient: {recipient}")
            print(f"subject: {subject}")
            print(f"sender: {sender}")
            print(f"content: {html}")
