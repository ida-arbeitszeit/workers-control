from dataclasses import dataclass
from uuid import UUID

from workers_control.core.interactors.get_private_consumption_details import (
    GetPrivateConsumptionDetailsInteractor,
)
from workers_control.web.session import Session


@dataclass
class GetPrivateConsumptionDetailsController:
    session: Session

    def create_request(
        self, consumption_id: UUID
    ) -> GetPrivateConsumptionDetailsInteractor.Request:
        member = self.session.get_current_user()
        assert member
        return GetPrivateConsumptionDetailsInteractor.Request(
            consumption_id=consumption_id,
            member=member,
        )
