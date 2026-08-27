from dataclasses import dataclass
from uuid import UUID

import flask

from workers_control.core.interactors.deny_collaboration import (
    DenyCollaborationInteractor,
    DenyCollaborationRequest,
)
from workers_control.db import commit_changes
from workers_control.flask.flask_session import FlaskSession
from workers_control.flask.types import Response
from workers_control.web.www.presenters.deny_collaboration_presenter import (
    DenyCollaborationPresenter,
)


@dataclass
class DenyCollaborationView:
    interactor: DenyCollaborationInteractor
    presenter: DenyCollaborationPresenter
    flask_session: FlaskSession

    @commit_changes
    def POST(self) -> Response:
        form = flask.request.form
        collaboration_id = UUID(form["collaboration_id"].strip())
        plan_id = UUID(form["plan_id"].strip())
        current_user = self.flask_session.get_current_user()
        assert current_user
        deny_collaboration_response = self.interactor.execute(
            DenyCollaborationRequest(
                current_user,
                plan_id,
                collaboration_id,
            )
        )
        view_model = self.presenter.render_response(deny_collaboration_response)
        return flask.redirect(view_model.redirection_url)
