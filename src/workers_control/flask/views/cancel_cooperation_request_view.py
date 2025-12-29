from dataclasses import dataclass
from uuid import UUID

import flask

from workers_control.core.interactors.cancel_cooperation_solicitation import (
    CancelCooperationSolicitationInteractor,
    CancelCooperationSolicitationRequest,
)
from workers_control.db import commit_changes
from workers_control.flask.flask_session import FlaskSession
from workers_control.flask.types import Response
from workers_control.web.www.presenters.cancel_cooperation_request_presenter import (
    CancelCooperationRequestPresenter,
)


@dataclass
class CancelCooperationRequestView:
    interactor: CancelCooperationSolicitationInteractor
    presenter: CancelCooperationRequestPresenter
    flask_session: FlaskSession

    @commit_changes
    def POST(self) -> Response:
        current_user = self.flask_session.get_current_user()
        assert current_user
        plan_id = UUID(flask.request.form["plan_id"])
        requester_id = current_user
        uc_response = self.interactor.execute(
            CancelCooperationSolicitationRequest(requester_id, plan_id)
        )
        view_model = self.presenter.render_response(uc_response)
        return flask.redirect(view_model.redirection_url)
