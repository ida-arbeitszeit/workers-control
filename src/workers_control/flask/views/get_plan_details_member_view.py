from dataclasses import dataclass
from uuid import UUID

from flask import Response as FlaskResponse
from flask import render_template

from workers_control.core.interactors.get_plan_details import GetPlanDetailsInteractor
from workers_control.flask.types import Response
from workers_control.flask.views.http_error_view import http_404
from workers_control.web.www.presenters.get_plan_details_member_presenter import (
    GetPlanDetailsMemberMemberPresenter,
)


@dataclass
class GetPlanDetailsMemberView:
    interactor: GetPlanDetailsInteractor
    presenter: GetPlanDetailsMemberMemberPresenter

    def GET(self, plan_id: UUID) -> Response:
        interactor_request = GetPlanDetailsInteractor.Request(plan_id)
        interactor_response = self.interactor.get_plan_details(interactor_request)
        if interactor_response:
            view_model = self.presenter.present(interactor_response)
            return FlaskResponse(
                render_template(
                    "member/plan_details.html",
                    view_model=view_model,
                )
            )
        else:
            return http_404()
