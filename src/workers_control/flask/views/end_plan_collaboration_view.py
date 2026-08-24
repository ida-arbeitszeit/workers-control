from dataclasses import dataclass
from uuid import UUID

import flask

from workers_control.core.interactors.end_collaboration import (
    EndCollaborationInteractor,
    EndCollaborationRequest,
)
from workers_control.db import commit_changes
from workers_control.flask.flask_session import FlaskSession
from workers_control.flask.types import Response
from workers_control.web.www.presenters.end_plan_collaboration_presenter import (
    EndPlanCollaborationPresenter,
)


@dataclass
class EndPlanCollaborationView:
    interactor: EndCollaborationInteractor
    presenter: EndPlanCollaborationPresenter
    flask_session: FlaskSession

    @commit_changes
    def POST(self) -> Response:
        form = flask.request.form
        current_user = self.flask_session.get_current_user()
        assert current_user
        collaboration_id = UUID(form["collaboration_id"].strip())
        plan_id = UUID(form["plan_id"].strip())
        response = self.interactor.execute(
            EndCollaborationRequest(
                requester_id=current_user,
                plan_id=plan_id,
                collaboration_id=collaboration_id,
            )
        )
        view_model = self.presenter.render_response(response)
        return flask.redirect(view_model.redirection_url)
