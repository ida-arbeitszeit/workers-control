from dataclasses import dataclass
from uuid import UUID

from flask import redirect

from workers_control.core.interactors.create_draft_from_plan import (
    CreateDraftFromPlanInteractor,
)
from workers_control.db import commit_changes
from workers_control.flask.flask_request import FlaskRequest
from workers_control.flask.types import Response
from workers_control.web.www.controllers.create_draft_from_plan_controller import (
    CreateDraftFromPlanController,
)
from workers_control.web.www.presenters.create_draft_from_plan_presenter import (
    CreateDraftFromPlanPresenter,
)


@dataclass
class CreateDraftFromPlanView:
    interactor: CreateDraftFromPlanInteractor
    controller: CreateDraftFromPlanController
    presenter: CreateDraftFromPlanPresenter

    @commit_changes
    def POST(self, plan_id: UUID) -> Response:
        uc_request = self.controller.create_interactor_request(plan_id)
        uc_response = self.interactor.create_draft_from_plan(uc_request)
        view_model = self.presenter.render_response(
            interactor_response=uc_response,
            request=FlaskRequest(),
        )
        return redirect(view_model.redirect_url)
