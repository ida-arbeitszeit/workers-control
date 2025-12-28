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
from workers_control.web.www.presenters.accept_cooperation_request_presenter import (
    AcceptCooperationRequestPresenter,
)


@dataclass
class AcceptCooperationRequestView:
    interactor: AcceptCooperationInteractor
    presenter: AcceptCooperationRequestPresenter
    flask_session: FlaskSession

    @commit_changes
    def POST(self) -> Response:
        form = flask.request.form
        current_user = self.flask_session.get_current_user()
        assert current_user
        cooperation_id = UUID(form["cooperation_id"].strip())
        plan_id = UUID(form["plan_id"].strip())
        uc_request = AcceptCooperationRequest(
            requester_id=current_user,
            plan_id=plan_id,
            cooperation_id=cooperation_id,
        )
        uc_response = self.interactor.execute(uc_request)
        view_model = self.presenter.render_response(uc_response)
        return flask.redirect(view_model.redirection_url)
