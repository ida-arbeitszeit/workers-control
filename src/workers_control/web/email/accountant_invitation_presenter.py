from dataclasses import dataclass
from typing import List, Protocol

from workers_control.web.email import EmailConfiguration
from workers_control.web.token import TokenService
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex


@dataclass
class ViewModel:
    subject: str
    recipients: List[str]
    sender: str
    registration_link_url: str


class AccountantInvitationEmailView(Protocol):
    def render_accountant_invitation_email(self, view_model: ViewModel) -> None: ...


@dataclass
class AccountantInvitationEmailPresenter:
    invitation_view: AccountantInvitationEmailView
    email_configuration: EmailConfiguration
    translator: Translator
    url_index: UrlIndex
    token_service: TokenService

    def send_accountant_invitation(self, email: str) -> None:
        token = self.token_service.generate_token(email)
        view_model = ViewModel(
            subject=self.translator.gettext("Invitation to Workers Control app"),
            recipients=[email],
            sender=self.email_configuration.get_sender_address(),
            registration_link_url=self.url_index.get_accountant_invitation_url(token),
        )
        self.invitation_view.render_accountant_invitation_email(view_model)
