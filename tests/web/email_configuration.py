from workers_control.core.injector import singleton


@singleton
class FakeEmailConfiguration:
    def __init__(self) -> None:
        self._admin_email_address: str | None = None

    def set_admin_email_address(self, email_address: str) -> None:
        self._admin_email_address = email_address

    def get_sender_address(self) -> str:
        return "test@test.test"

    def get_admin_email_address(self) -> str | None:
        return self._admin_email_address
