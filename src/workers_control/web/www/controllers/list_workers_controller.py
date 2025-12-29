from dataclasses import dataclass

from workers_control.core.interactors import list_workers
from workers_control.web.session import Session


@dataclass
class ListWorkersController:
    session: Session

    def create_interactor_request(self) -> list_workers.Request:
        current_user = self.session.get_current_user()
        assert current_user
        return list_workers.Request(company=current_user)
