from typing import Optional

from workers_control.core.injector import singleton
from workers_control.web.email.accountant_invitation_presenter import ViewModel


@singleton
class AccountantInvitationEmailViewImpl:
    def __init__(self) -> None:
        self.view_model: Optional[ViewModel] = None

    def render_accountant_invitation_email(self, view_model: ViewModel) -> None:
        self.view_model = view_model

    def get_view_model(self) -> ViewModel:
        assert self.view_model
        return self.view_model
