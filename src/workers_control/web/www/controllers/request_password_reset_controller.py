from dataclasses import dataclass
from typing import Optional

from workers_control.core.interactors import request_user_password_reset
from workers_control.core.repositories import DatabaseGateway
from workers_control.web.token import TokenService


@dataclass
class RequestPasswordResetController:
    database: DatabaseGateway
    token_service: TokenService

    def create_password_reset_request(
        self, email_address: str
    ) -> Optional[request_user_password_reset.Request]:
        if not self._account_exists(email_address):
            return None
        token = self.token_service.generate_token(email_address)
        return request_user_password_reset.Request(
            email_address=email_address,
            reset_token=token,
        )

    def _account_exists(self, email_address: str) -> bool:
        return bool(
            self.database.get_account_credentials()
            .with_email_address(email_address)
            .first()
        )
