from dataclasses import dataclass

from workers_control.core.interactors import list_basic_services_of_worker as interactor
from workers_control.web.session import Session, UserRole


@dataclass
class InvalidRequest:
    status_code: int


@dataclass
class ListBasicServicesOfWorkerController:
    session: Session

    def process_request(self) -> interactor.Request | InvalidRequest:
        user_id = self.session.get_current_user()
        if not user_id:
            return InvalidRequest(status_code=401)
        match self.session.get_user_role():
            case UserRole.member:
                return interactor.Request(member=user_id)
        return InvalidRequest(status_code=403)
