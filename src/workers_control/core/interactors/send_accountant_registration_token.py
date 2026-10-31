import enum
from dataclasses import dataclass

from workers_control.core.email import is_possibly_an_email_address
from workers_control.core.email_notifications import AccountantInvitation, EmailSender
from workers_control.core.repositories import DatabaseGateway


@dataclass
class RejectionReason(enum.Enum):
    invalid_email_address = enum.auto()
    user_exists_already = enum.auto()


@dataclass
class SendAccountantRegistrationTokenInteractor:
    @dataclass
    class Response:
        rejection_reason: RejectionReason | None

        @property
        def is_success(self) -> bool:
            return self.rejection_reason is None

    @dataclass
    class Request:
        email: str

    email_sender: EmailSender
    database: DatabaseGateway

    def send_accountant_registration_token(self, request: Request) -> Response:
        email = request.email
        if not is_possibly_an_email_address(email):
            return self.Response(rejection_reason=RejectionReason.invalid_email_address)
        if self._is_user_existing(email):
            return self.Response(rejection_reason=RejectionReason.user_exists_already)
        self.email_sender.send_email(AccountantInvitation(email_address=request.email))
        return self.Response(rejection_reason=None)

    def _is_user_existing(self, email: str) -> bool:
        return bool(self.database.get_accountants().with_email_address(email))
