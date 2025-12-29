from dataclasses import dataclass
from datetime import timedelta
from typing import Protocol

from workers_control.core.interactors.register_accountant import (
    RegisterAccountantInteractor,
)
from workers_control.web.token import TokenService


class RegisterAccountantForm(Protocol):
    def get_name(self) -> str: ...

    def get_password(self) -> str: ...

    def get_email_address(self) -> str: ...


@dataclass
class RegisterAccountantController:
    token_service: TokenService

    def create_interactor_request(
        self, form: RegisterAccountantForm
    ) -> RegisterAccountantInteractor.Request:
        return RegisterAccountantInteractor.Request(
            name=form.get_name(),
            email=form.get_email_address(),
            password=form.get_password(),
        )

    def extract_token(self, token: str) -> str | None:
        return self.token_service.confirm_token(token, timedelta(days=1))
