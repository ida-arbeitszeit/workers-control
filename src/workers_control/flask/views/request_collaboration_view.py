from dataclasses import dataclass

from flask import Response, redirect, render_template

from workers_control.core.interactors.list_active_plans_of_company import (
    ListActivePlansOfCompanyInteractor,
)
from workers_control.core.interactors.request_collaboration import (
    RequestCollaborationInteractor,
    RequestCollaborationRequest,
)
from workers_control.db import commit_changes
from workers_control.flask import types
from workers_control.flask.flask_request import FlaskRequest
from workers_control.flask.flask_session import FlaskSession
from workers_control.flask.views.http_error_view import http_404
from workers_control.web.forms import RequestCollaborationForm
from workers_control.web.www.controllers.request_collaboration_controller import (
    RequestCollaborationController,
)
from workers_control.web.www.presenters.list_plans_presenter import (
    ListPlansPresenter,
    ListPlansViewModel,
)
from workers_control.web.www.presenters.request_collaboration_presenter import (
    RequestCollaborationPresenter,
    RequestCollaborationViewModel,
)


@dataclass
class RequestCollaborationView:
    list_plans: ListActivePlansOfCompanyInteractor
    list_plans_presenter: ListPlansPresenter
    request_collaboration: RequestCollaborationInteractor
    controller: RequestCollaborationController
    presenter: RequestCollaborationPresenter
    flask_session: FlaskSession

    def GET(self) -> types.Response:
        return self._render_template(
            form=RequestCollaborationForm(plan_id_value="", collaboration_id_value="")
        )

    @commit_changes
    def POST(self) -> types.Response:
        match self.controller.import_form_data(FlaskRequest()):
            case None:
                return http_404()
            case RequestCollaborationForm() as form:
                return self._render_template(form=form, status=400)
            case RequestCollaborationRequest() as interactor_request:
                pass
        interactor_response = self.request_collaboration.execute(interactor_request)
        view_model = self.presenter.present(interactor_response)
        if view_model.redirect_url:
            return redirect(view_model.redirect_url)
        return self._render_template(
            form=RequestCollaborationForm(
                plan_id_value=str(interactor_request.plan_id),
                collaboration_id_value=str(interactor_request.collaboration_id),
            ),
            view_model=view_model,
            status=400,
        )

    def _get_list_plans_view_model(self) -> ListPlansViewModel:
        current_user = self.flask_session.get_current_user()
        assert current_user
        plans_list_response = self.list_plans.execute(current_user)
        list_plans_view_model = self.list_plans_presenter.present(plans_list_response)
        return list_plans_view_model

    def _render_template(
        self,
        form: RequestCollaborationForm,
        view_model: RequestCollaborationViewModel | None = None,
        status: int = 200,
    ) -> types.Response:
        return Response(
            render_template(
                "company/request_collaboration.html",
                form=form,
                view_model=view_model,
                list_plans_view_model=self._get_list_plans_view_model(),
                navbar_items=self.presenter.create_navbar_items(),
            ),
            status=status,
        )
