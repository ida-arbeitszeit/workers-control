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
    @dataclass
    class Result:
        request: RegisterAccountantInteractor.Request
        token_email: str

    token_service: TokenService

    def create_interactor_request(
        self, form: RegisterAccountantForm, token: str
    ) -> Result | None:
        token_email = self.token_service.confirm_token(token, timedelta(days=1))
        if token_email is None:
            return None
        return self.Result(
            request=RegisterAccountantInteractor.Request(
                name=form.get_name(),
                email=form.get_email_address(),
                password=form.get_password(),
            ),
            token_email=token_email,
        )
