from dataclasses import dataclass, field
from datetime import timedelta
from typing import List, Optional, Tuple
from uuid import UUID

from tests.base_test_case import BaseTestCase
from tests.datetime_service import datetime_utc
from tests.interactors.repositories import MockDatabase
from workers_control.email_sending_worker.interface import EmailSenderPlugin
from workers_control.email_sending_worker.worker import EmailWorker


@dataclass
class CapturingMailService(EmailSenderPlugin):
    sent: List[Tuple[str, list[str], str, str]] = field(default_factory=list)
    fail_with: Optional[Exception] = None

    def send_message(
        self, subject: str, recipient: list[str], html: str, sender: str
    ) -> None:
        if self.fail_with is not None:
            raise self.fail_with
        self.sent.append((subject, recipient, html, sender))


class EmailWorkerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.mail_service = CapturingMailService()
        self.commits = 0
        self.database = self.injector.get(MockDatabase)
        self.datetime_service.freeze_time(datetime_utc(2026, 1, 1, 12, 0))
        self.worker = EmailWorker(
            mail_service=self.mail_service,
            database_gateway=self.database_gateway,
            datetime_service=self.datetime_service,
            commit=self._commit,
            batch_size=5,
        )

    def _commit(self) -> None:
        self.commits += 1

    def _create_email(self, recipient: str = "to@example.org") -> UUID:
        record = self.database_gateway.create_email(
            created_at=self.datetime_service.now(),
            recipient=recipient,
            sender="from@example.org",
            subject="hello",
            html="<p>hi</p>",
        )
        return record.id

    def test_run_once_returns_zero_when_outbox_empty(self) -> None:
        self.assertEqual(self.worker.run_once(), 0)

    def test_pending_email_is_sent_and_marked_sent(self) -> None:
        email_id = self._create_email()
        sent = self.worker.run_once()
        self.assertEqual(sent, 1)
        self.assertEqual(len(self.mail_service.sent), 1)
        status = self.database.email_outbox_status[email_id]
        self.assertEqual(status.sent_at, self.datetime_service.now())
        self.assertEqual(status.retry_count, 0)
        self.assertIsNone(status.last_error)

    def test_already_sent_email_is_not_resent(self) -> None:
        self._create_email()
        self.worker.run_once()
        self.mail_service.sent.clear()
        sent_again = self.worker.run_once()
        self.assertEqual(sent_again, 0)
        self.assertEqual(self.mail_service.sent, [])

    def test_smtp_failure_increments_retry_count_and_records_error(self) -> None:
        email_id = self._create_email()
        self.mail_service.fail_with = RuntimeError("smtp boom")
        self.worker.run_once()
        status = self.database.email_outbox_status[email_id]
        self.assertIsNone(status.sent_at)
        self.assertEqual(status.retry_count, 1)
        self.assertEqual(status.last_error, "smtp boom")

    def test_failed_email_is_retried_on_next_run(self) -> None:
        self._create_email()
        self.mail_service.fail_with = RuntimeError("smtp boom")
        self.worker.run_once()
        self.mail_service.fail_with = None
        sent = self.worker.run_once()
        self.assertEqual(sent, 1)

    def test_batch_size_limits_emails_processed_per_run(self) -> None:
        for i in range(10):
            self._create_email(recipient=f"to{i}@example.org")
        sent = self.worker.run_once()
        self.assertEqual(sent, 5)

    def test_emails_are_processed_in_creation_order(self) -> None:
        self._create_email(recipient="first@example.org")
        self.datetime_service.advance_time(timedelta(seconds=1))
        self._create_email(recipient="second@example.org")
        self.worker.run_once()
        recipients_sent_in_order = [args[1] for args in self.mail_service.sent]
        self.assertEqual(
            recipients_sent_in_order,
            [["first@example.org"], ["second@example.org"]],
        )

    def test_recipient_string_is_split_into_list_for_smtp(self) -> None:
        self._create_email(recipient="a@example.org,b@example.org")
        self.worker.run_once()
        self.assertEqual(
            self.mail_service.sent[0][1], ["a@example.org", "b@example.org"]
        )

    def test_commit_is_called_after_processing_a_batch(self) -> None:
        self._create_email()
        self.worker.run_once()
        self.assertEqual(self.commits, 1)

    def test_commit_is_not_called_when_no_emails_to_process(self) -> None:
        self.worker.run_once()
        self.assertEqual(self.commits, 0)
