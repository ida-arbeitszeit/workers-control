from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

from workers_control.core.interactors.confirm_company import (
    ConfirmCompanyInteractor as Interactor,
)
from workers_control.web.token import TokenService


@dataclass
class ConfirmCompanyController:
    token_service: TokenService

    def process_request(self, token: str) -> Optional[Interactor.Request]:
        email_address = self.token_service.confirm_token(
            token, max_age=timedelta(days=1)
        )
        if not email_address:
            return None
        return Interactor.Request(email_address=email_address)
