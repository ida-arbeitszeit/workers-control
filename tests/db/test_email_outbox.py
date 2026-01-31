from tests.db.base_test_case import DatabaseTestCase


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
