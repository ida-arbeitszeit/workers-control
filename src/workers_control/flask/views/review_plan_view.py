from dataclasses import dataclass
from uuid import UUID

from flask import Response as FlaskResponse
from flask import redirect, render_template

from workers_control.core.interactors.approve_plan import ApprovePlanInteractor
from workers_control.core.interactors.get_plan_for_review import (
    GetPlanForReviewInteractor,
)
from workers_control.core.interactors.reject_plan import RejectPlanInteractor
from workers_control.db import commit_changes
from workers_control.flask.flask_request import FlaskRequest
from workers_control.flask.types import Response
from workers_control.flask.views.http_error_view import http_404
from workers_control.web.www.controllers.review_plan_controller import (
    ReviewDecision,
    ReviewPlanController,
)
from workers_control.web.www.presenters.approve_plan_presenter import (
    ApprovePlanPresenter,
)
from workers_control.web.www.presenters.get_plan_for_review_presenter import (
    GetPlanForReviewPresenter,
)
from workers_control.web.www.presenters.reject_plan_presenter import RejectPlanPresenter


@dataclass
class ReviewPlanView:
    get_interactor: GetPlanForReviewInteractor
    get_presenter: GetPlanForReviewPresenter
    controller: ReviewPlanController
    approve_interactor: ApprovePlanInteractor
    approve_presenter: ApprovePlanPresenter
    reject_interactor: RejectPlanInteractor
    reject_presenter: RejectPlanPresenter

    def GET(self, plan_id: UUID) -> Response:
        return self._render_review_page(plan_id, status_code=200)

    @commit_changes
    def POST(self, plan_id: UUID) -> Response:
        match self.controller.process_review_form(FlaskRequest()):
            case ReviewDecision.approve:
                approve_response = self.approve_interactor.approve_plan(
                    ApprovePlanInteractor.Request(plan=plan_id)
                )
                approve_view_model = self.approve_presenter.approve_plan(
                    approve_response
                )
                return redirect(approve_view_model.redirect_url)
            case ReviewDecision.reject:
                reject_response = self.reject_interactor.reject_plan(
                    RejectPlanInteractor.Request(plan=plan_id)
                )
                reject_view_model = self.reject_presenter.reject_plan(reject_response)
                return redirect(reject_view_model.redirect_url)
            case None:
                return self._render_review_page(plan_id, status_code=400)

    def _render_review_page(self, plan_id: UUID, status_code: int) -> Response:
        interactor_response = self.get_interactor.get_plan_for_review(
            GetPlanForReviewInteractor.Request(plan=plan_id)
        )
        if interactor_response is None:
            return http_404()
        view_model = self.get_presenter.present(interactor_response)
        return FlaskResponse(
            render_template(
                "accountant/review_plan.html",
                view_model=view_model,
            ),
            status=status_code,
        )
