from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import redirect, render_template, request, url_for

from workers_control.core.interactors.create_collaboration import (
    CreateCollaborationInteractor,
    CreateCollaborationRequest,
)
from workers_control.db import commit_changes
from workers_control.flask.flask_session import FlaskSession
from workers_control.flask.forms import CreateCollaborationForm
from workers_control.flask.types import Response
from workers_control.web.www.presenters.create_collaboration_presenter import (
    CreateCollaborationPresenter,
)


@dataclass
class CreateCollaborationView:
    interactor: CreateCollaborationInteractor
    presenter: CreateCollaborationPresenter
    session: FlaskSession

    def GET(self) -> Response:
        return FlaskResponse(
            self._render_template(CreateCollaborationForm()), status=200
        )

    @commit_changes
    def POST(self) -> Response:
        form = CreateCollaborationForm(request.form)
        name = form.get_name_string()
        definition = form.get_definition_string()
        user = self.session.get_current_user()
        assert name
        assert definition
        assert user
        interactor_request = CreateCollaborationRequest(user, name, definition)
        interactor_response = self.interactor.execute(interactor_request)
        self.presenter.present(interactor_response)
        if interactor_response.is_rejected:
            return FlaskResponse(self._render_template(form), status=400)
        return redirect(url_for("main_company.my_collaborations"))

    def _render_template(self, form: CreateCollaborationForm) -> str:
        return render_template(
            "company/create_collaboration.html",
            form=form,
            navbar_items=self.presenter.create_navbar_items(),
        )
