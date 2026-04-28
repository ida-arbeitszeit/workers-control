from dataclasses import dataclass
from uuid import UUID

from workers_control.core.interactors.get_productive_consumption_details import (
    GetProductiveConsumptionDetailsInteractor,
)
from workers_control.web.session import Session


@dataclass
class GetProductiveConsumptionDetailsController:
    session: Session

    def create_request(
        self, consumption_id: UUID
    ) -> GetProductiveConsumptionDetailsInteractor.Request:
        company = self.session.get_current_user()
        assert company
        return GetProductiveConsumptionDetailsInteractor.Request(
            consumption_id=consumption_id,
            company=company,
        )
