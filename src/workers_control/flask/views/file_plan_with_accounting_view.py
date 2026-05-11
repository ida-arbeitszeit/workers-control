from dataclasses import dataclass

from flask import redirect

from workers_control.core.interactors.file_plan_with_accounting import (
    FilePlanWithAccounting,
)
from workers_control.db import commit_changes
from workers_control.flask.flask_session import FlaskSession
from workers_control.flask.types import Response
from workers_control.flask.views.http_error_view import http_404
from workers_control.web.www.controllers.file_plan_with_accounting_controller import (
    FilePlanWithAccountingController,
)
from workers_control.web.www.presenters.file_plan_with_accounting_presenter import (
    FilePlanWithAccountingPresenter,
)


@dataclass
class FilePlanWithAccountingView:
    session: FlaskSession
    controller: FilePlanWithAccountingController
    interactor: FilePlanWithAccounting
    presenter: FilePlanWithAccountingPresenter

    @commit_changes
    def POST(self, draft_id: str) -> Response:
        try:
            request = self.controller.process_file_plan_with_accounting_request(
                draft_id=draft_id, session=self.session
            )
        except self.controller.InvalidRequest:
            return http_404()
        response = self.interactor.file_plan_with_accounting(request)
        view_model = self.presenter.present_response(response)
        return redirect(view_model.redirect_url)
