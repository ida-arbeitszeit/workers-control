from datetime import timedelta
from uuid import UUID

from tests.db.base_test_case import DatabaseTestCase
from workers_control.db import models


class CreateOutboundEmailTests(DatabaseTestCase):
    def test_that_outbound_email_can_be_stored(self) -> None:
        self.create_valid_email()

    def create_valid_email(self) -> None:
        self.database_gateway.create_email(
            created_at=self.datetime_service.now(),
            recipient="some_recipient@test.org",
            sender="some_sender@test.org",
            subject="Some Subject",
            html="<p>Some HTML content</p>",
        )


class GetEmailsTests(DatabaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.datetime_service.freeze_time()

    def _create_email(self, recipient: str = "to@test.org") -> UUID:
        return self.database_gateway.create_email(
            created_at=self.datetime_service.now(),
            recipient=recipient,
            sender="from@test.org",
            subject="subj",
            html="<p>body</p>",
        ).id

    def test_get_emails_returns_all_created_emails(self) -> None:
        self._create_email("a@test.org")
        self._create_email("b@test.org")
        self.assertEqual(len(self.database_gateway.get_emails()), 2)

    def test_with_id_filters_to_a_single_email(self) -> None:
        email_id = self._create_email()
        self._create_email("other@test.org")
        result = list(self.database_gateway.get_emails().with_id(email_id))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, email_id)

    def test_that_have_not_been_sent_excludes_sent_emails(self) -> None:
        sent_id = self._create_email()
        self._create_email("pending@test.org")
        self.database_gateway.get_emails().with_id(sent_id).update().set_sent_at(
            self.datetime_service.now()
        ).perform()
        unsent = list(
            self.database_gateway.get_emails()
            .that_have_not_been_sent()
            .ordered_by_creation_date()
        )
        self.assertEqual(len(unsent), 1)
        self.assertEqual(unsent[0].recipient, "pending@test.org")

    def test_ordered_by_creation_date_ascending_returns_oldest_first(self) -> None:
        self._create_email("first@test.org")
        self.datetime_service.advance_time(timedelta(seconds=1))
        self._create_email("second@test.org")
        ordered = list(
            self.database_gateway.get_emails().ordered_by_creation_date(ascending=True)
        )
        self.assertEqual(
            [e.recipient for e in ordered], ["first@test.org", "second@test.org"]
        )

    def test_ordered_by_creation_date_descending_returns_newest_first(self) -> None:
        self._create_email("first@test.org")
        self.datetime_service.advance_time(timedelta(seconds=1))
        self._create_email("second@test.org")
        ordered = list(
            self.database_gateway.get_emails().ordered_by_creation_date(ascending=False)
        )
        self.assertEqual(
            [e.recipient for e in ordered], ["second@test.org", "first@test.org"]
        )


class EmailUpdateTests(DatabaseTestCase):
    def _create_email(self) -> UUID:
        return self.database_gateway.create_email(
            created_at=self.datetime_service.now(),
            recipient="to@test.org",
            sender="from@test.org",
            subject="subj",
            html="<p>body</p>",
        ).id

    def test_set_sent_at_marks_email_as_sent(self) -> None:
        email_id = self._create_email()
        self.datetime_service.freeze_time()
        sent_at = self.datetime_service.now()
        affected = (
            self.database_gateway.get_emails()
            .with_id(email_id)
            .update()
            .set_sent_at(sent_at)
            .perform()
        )
        self.assertEqual(affected, 1)
        unsent = list(
            self.database_gateway.get_emails()
            .that_have_not_been_sent()
            .with_id(email_id)
        )
        self.assertEqual(unsent, [])

    def test_increment_retry_count_increments_each_time(self) -> None:
        email_id = self._create_email()
        for _ in range(3):
            (
                self.database_gateway.get_emails()
                .with_id(email_id)
                .update()
                .increment_retry_count()
                .perform()
            )
        orm = self.db.session.query(models.EmailOutbox).filter_by(id=email_id).one()
        self.assertEqual(orm.retry_count, 3)

    def test_set_last_error_records_error_message(self) -> None:
        email_id = self._create_email()
        (
            self.database_gateway.get_emails()
            .with_id(email_id)
            .update()
            .set_last_error("smtp boom")
            .perform()
        )
        orm = self.db.session.query(models.EmailOutbox).filter_by(id=email_id).one()
        self.assertEqual(orm.last_error, "smtp boom")

    def test_chained_updates_apply_in_one_perform(self) -> None:
        email_id = self._create_email()
        (
            self.database_gateway.get_emails()
            .with_id(email_id)
            .update()
            .set_last_error("err")
            .increment_retry_count()
            .perform()
        )
        orm = self.db.session.query(models.EmailOutbox).filter_by(id=email_id).one()
        self.assertEqual(orm.last_error, "err")
        self.assertEqual(orm.retry_count, 1)

    def test_perform_with_no_setters_returns_zero(self) -> None:
        self._create_email()
        affected = self.database_gateway.get_emails().update().perform()
        self.assertEqual(affected, 0)
