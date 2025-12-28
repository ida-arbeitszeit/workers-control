from dataclasses import dataclass
from uuid import UUID

from workers_control.core.interactors.accept_coordination_transfer import (
    AcceptCoordinationTransferInteractor,
)
from workers_control.web.session import Session

InteractorRequest = AcceptCoordinationTransferInteractor.Request


@dataclass
class AcceptCoordinationTransferController:
    session: Session

    def create_interactor_request(self, transfer_request: UUID) -> InteractorRequest:
        current_user = self.session.get_current_user()
        assert current_user
        return InteractorRequest(
            transfer_request_id=transfer_request, accepting_company=current_user
        )
