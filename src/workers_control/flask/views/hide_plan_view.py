from dataclasses import dataclass
from uuid import UUID

from flask import redirect, url_for

from workers_control.core.interactors.hide_plan import HidePlanInteractor
from workers_control.db import commit_changes
from workers_control.flask.types import Response
from workers_control.web.www.presenters.hide_plan_presenter import HidePlanPresenter


@dataclass
class HidePlanView:
    interactor: HidePlanInteractor
    presenter: HidePlanPresenter

    @commit_changes
    def GET(self, plan_id: UUID) -> Response:
        return self._execute(plan_id)

    @commit_changes
    def POST(self, plan_id: UUID) -> Response:
        return self._execute(plan_id)

    def _execute(self, plan_id: UUID) -> Response:
        response = self.interactor.execute(plan_id)
        self.presenter.present(response)
        return redirect(url_for("main_company.my_plans"))
