from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Iterator

from workers_control.core import records
from workers_control.core.datetime_service import DatetimeService
from workers_control.core.repositories import DatabaseGateway
from workers_control.flask.mail_service.interface import EmailPlugin


@dataclass
class MockEmailService(EmailPlugin):
    database_gateway: DatabaseGateway
    datetime_service: DatetimeService
    _recording_outboxes: list[list[records.Email]] = field(default_factory=list)

    def send_message(
        self,
        subject: str,
        recipients: list[str],
        html: str,
        sender: str,
    ) -> None:
        for recipient in recipients:
            now = self.datetime_service.now()
            email = self.database_gateway.create_email(
                created_at=now,
                recipient=recipient,
                sender=sender,
                subject=subject,
                html=html,
            )
            for outbox in self._recording_outboxes:
                outbox.append(email)

    @contextmanager
    def record_messages(self) -> Iterator[list[records.Email]]:
        outbox: list[records.Email] = []
        self._recording_outboxes.append(outbox)
        try:
            yield outbox
        finally:
            self._recording_outboxes.remove(outbox)
