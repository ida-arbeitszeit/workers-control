from dataclasses import dataclass
from uuid import UUID

from flask import redirect

from workers_control.core.interactors.delete_draft import DeleteDraftInteractor
from workers_control.db import commit_changes
from workers_control.flask.flask_request import FlaskRequest
from workers_control.flask.types import Response
from workers_control.flask.views.http_error_view import http_404
from workers_control.web.www.controllers.delete_draft_controller import (
    DeleteDraftController,
)
from workers_control.web.www.presenters.delete_draft_presenter import (
    DeleteDraftPresenter,
)


@dataclass
class DeleteDraftView:
    controller: DeleteDraftController
    interactor: DeleteDraftInteractor
    presenter: DeleteDraftPresenter

    @commit_changes
    def POST(self, draft_id: UUID) -> Response:
        interactor_request = self.controller.get_request(
            request=FlaskRequest(), draft=draft_id
        )
        try:
            interactor_response = self.interactor.delete_draft(interactor_request)
        except self.interactor.Failure:
            return http_404()
        view_model = self.presenter.present_draft_deletion(interactor_response)
        return redirect(view_model.redirect_target)
