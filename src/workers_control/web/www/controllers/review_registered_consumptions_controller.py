from dataclasses import dataclass

from workers_control.core.interactors.review_registered_consumptions import (
    ReviewRegisteredConsumptionsInteractor,
)
from workers_control.web.session import Session, UserRole


@dataclass
class InvalidRequest:
    status_code: int


@dataclass
class ReviewRegisteredConsumptionsController:
    session: Session

    def create_interactor_request(
        self,
    ) -> ReviewRegisteredConsumptionsInteractor.Request | InvalidRequest:
        user_id = self.session.get_current_user()
        if not user_id:
            return InvalidRequest(status_code=401)
        match self.session.get_user_role():
            case UserRole.company:
                return ReviewRegisteredConsumptionsInteractor.Request(
                    providing_company=user_id
                )
        return InvalidRequest(status_code=403)
