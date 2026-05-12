from dataclasses import dataclass
from uuid import UUID

from flask import redirect, url_for

from workers_control.core.interactors.revoke_plan_filing import (
    RevokePlanFilingInteractor,
)
from workers_control.db import commit_changes
from workers_control.flask.types import Response
from workers_control.web.www.controllers.revoke_plan_filing_controller import (
    RevokePlanFilingController,
)
from workers_control.web.www.presenters.revoke_plan_filing_presenter import (
    RevokePlanFilingPresenter,
)


@dataclass
class RevokePlanFilingView:
    controller: RevokePlanFilingController
    interactor: RevokePlanFilingInteractor
    presenter: RevokePlanFilingPresenter

    @commit_changes
    def POST(self, plan_id: UUID) -> Response:
        request = self.controller.create_request(plan_id=plan_id)
        response = self.interactor.revoke_plan_filing(request=request)
        self.presenter.present(response)
        return redirect(url_for("main_company.my_plans"))
