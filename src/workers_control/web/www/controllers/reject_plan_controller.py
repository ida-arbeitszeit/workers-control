from uuid import UUID

from workers_control.core.interactors.reject_plan import (
    RejectPlanInteractor as Interactor,
)


class RejectPlanController:
    def reject_plan(self, plan: UUID) -> Interactor.Request:
        return Interactor.Request(plan=plan)
