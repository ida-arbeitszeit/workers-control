from dataclasses import dataclass
from uuid import UUID

import flask

from workers_control.core.interactors.end_cooperation import (
    EndCooperationInteractor,
    EndCooperationRequest,
)
from workers_control.db import commit_changes
from workers_control.flask.flask_session import FlaskSession
from workers_control.flask.types import Response
from workers_control.web.www.presenters.end_plan_cooperation_presenter import (
    EndPlanCooperationPresenter,
)


@dataclass
class EndPlanCooperationView:
    interactor: EndCooperationInteractor
    presenter: EndPlanCooperationPresenter
    flask_session: FlaskSession

    @commit_changes
    def POST(self) -> Response:
        form = flask.request.form
        current_user = self.flask_session.get_current_user()
        assert current_user
        cooperation_id = UUID(form["cooperation_id"].strip())
        plan_id = UUID(form["plan_id"].strip())
        response = self.interactor.execute(
            EndCooperationRequest(
                requester_id=current_user,
                plan_id=plan_id,
                cooperation_id=cooperation_id,
            )
        )
        view_model = self.presenter.render_response(response)
        return flask.redirect(view_model.redirection_url)
