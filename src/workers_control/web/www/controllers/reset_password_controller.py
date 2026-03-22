from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

from workers_control.core.interactors import change_user_password
from workers_control.web.token import TokenService

PASSWORD_RESET_TOKEN_MAX_AGE = timedelta(minutes=15)


@dataclass
class ResetPasswordController:
    token_service: TokenService

    def validate_token(self, token: str) -> Optional[str]:
        return self.token_service.confirm_token(
            token, max_age=PASSWORD_RESET_TOKEN_MAX_AGE
        )

    def create_request(
        self, token: str, new_password: str
    ) -> Optional[change_user_password.Request]:
        email = self.validate_token(token)
        if email is None:
            return None
        return change_user_password.Request(
            email_address=email,
            new_password=new_password,
        )
