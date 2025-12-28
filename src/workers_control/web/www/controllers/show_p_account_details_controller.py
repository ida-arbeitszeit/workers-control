from dataclasses import dataclass
from uuid import UUID

from workers_control.core.interactors.show_p_account_details import (
    ShowPAccountDetailsInteractor,
)


@dataclass
class ShowPAccountDetailsController:
    def create_request(self, company: UUID) -> ShowPAccountDetailsInteractor.Request:
        return ShowPAccountDetailsInteractor.Request(company=company)
