from dataclasses import dataclass
from uuid import UUID

from workers_control.core.interactors.revoke_plan_filing import (
    RevokePlanFilingInteractor,
)
from workers_control.web.session import Session


@dataclass
class RevokePlanFilingController:
    session: Session

    def create_request(self, plan_id: UUID) -> RevokePlanFilingInteractor.Request:
        requester = self.session.get_current_user()
        assert requester
        return RevokePlanFilingInteractor.Request(plan=plan_id, requester=requester)
