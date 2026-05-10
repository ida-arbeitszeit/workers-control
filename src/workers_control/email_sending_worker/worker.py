"""Email sending worker.

Polls the email_outbox table for unsent emails, sends them via SMTP, and
records success or failure on each row. Designed to run as a separate process
from the Flask app — see `flask send-emails`.
"""

from __future__ import annotations

import logging
import signal
import time
from dataclasses import dataclass, field
from typing import Callable

from workers_control.core.datetime_service import DatetimeService
from workers_control.core.repositories import DatabaseGateway
from workers_control.email_sending_worker.interface import EmailSenderPlugin

logger = logging.getLogger(__name__)

DEFAULT_BATCH_SIZE = 5
DEFAULT_POLL_INTERVAL_SECONDS = 5.0


@dataclass
class EmailWorker:
    mail_service: EmailSenderPlugin
    database_gateway: DatabaseGateway
    datetime_service: DatetimeService
    commit: Callable[[], None]
    batch_size: int = DEFAULT_BATCH_SIZE
    poll_interval_seconds: float = DEFAULT_POLL_INTERVAL_SECONDS
    _running: bool = field(default=True, init=False, repr=False)

    def run_once(self) -> int:
        """Process one batch of unsent emails.

        Returns the number of emails that were sent successfully in this batch.
        """
        emails = list(
            self.database_gateway.get_emails()
            .that_have_not_been_sent()
            .ordered_by_creation_date()
            .limit(self.batch_size)
        )
        if not emails:
            return 0
        sent = 0
        for email in emails:
            row = self.database_gateway.get_emails().with_id(email.id)
            try:
                self.mail_service.send_message(
                    subject=email.subject,
                    recipient=email.recipient.split(","),
                    html=email.html,
                    sender=email.sender,
                )
            except Exception as exc:
                logger.warning(
                    "Failed to send email %s: %s", email.id, exc, exc_info=True
                )
                row.update().set_last_error(str(exc)).increment_retry_count().perform()
            else:
                row.update().set_sent_at(self.datetime_service.now()).perform()
                sent += 1
        self.commit()
        return sent

    def run(self) -> None:
        """Run the polling loop until SIGTERM/SIGINT is received."""
        self._install_signal_handlers()
        logger.info("Email worker started")
        while self._running:
            try:
                sent = self.run_once()
            except Exception:
                logger.exception("Unexpected error in email worker batch")
                sent = 0
            if sent < self.batch_size:
                # No full batch processed — wait before polling again.
                self._sleep_interruptible(self.poll_interval_seconds)
        logger.info("Email worker stopped")

    def stop(self) -> None:
        self._running = False

    def _install_signal_handlers(self) -> None:
        def handler(signum: int, frame: object) -> None:
            logger.info("Received signal %s, shutting down", signum)
            self.stop()

        signal.signal(signal.SIGTERM, handler)
        signal.signal(signal.SIGINT, handler)

    def _sleep_interruptible(self, seconds: float) -> None:
        end = time.monotonic() + seconds
        while self._running and time.monotonic() < end:
            time.sleep(min(0.5, end - time.monotonic()))
