from dataclasses import dataclass
from uuid import UUID

import flask

from workers_control.core.interactors.accept_cooperation import (
    AcceptCooperationInteractor,
    AcceptCooperationRequest,
)
from workers_control.db import commit_changes
from workers_control.flask.flask_session import FlaskSession
from workers_control.flask.types import Response
from workers_control.web.www.presenters.accept_collaboration_request_presenter import (
    AcceptCollaborationRequestPresenter,
)


@dataclass
class AcceptCollaborationRequestView:
    interactor: AcceptCooperationInteractor
    presenter: AcceptCollaborationRequestPresenter
    flask_session: FlaskSession

    @commit_changes
    def POST(self) -> Response:
        form = flask.request.form
        current_user = self.flask_session.get_current_user()
        assert current_user
        collaboration_id = UUID(form["collaboration_id"].strip())
        plan_id = UUID(form["plan_id"].strip())
        uc_request = AcceptCooperationRequest(
            requester_id=current_user,
            plan_id=plan_id,
            cooperation_id=collaboration_id,
        )
        uc_response = self.interactor.execute(uc_request)
        view_model = self.presenter.render_response(uc_response)
        return flask.redirect(view_model.redirection_url)
