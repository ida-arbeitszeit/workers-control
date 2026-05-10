from dataclasses import dataclass

from workers_control.core.datetime_service import DatetimeService
from workers_control.core.repositories import DatabaseGateway

from .interface import EmailPlugin


@dataclass
class MailStorageService(EmailPlugin):
    database_gateway: DatabaseGateway
    datetime_service: DatetimeService

    def send_message(
        self,
        subject: str,
        recipients: list[str],
        html: str,
        sender: str,
    ) -> None:
        self.database_gateway.create_email(
            created_at=self.datetime_service.now(),
            recipient=",".join(recipients),
            sender=sender,
            subject=subject,
            html=html,
        )
