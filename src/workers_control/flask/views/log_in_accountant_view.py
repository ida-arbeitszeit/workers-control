from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import redirect, render_template, request, url_for

from workers_control.core.interactors.log_in_accountant import LogInAccountantInteractor
from workers_control.db import commit_changes
from workers_control.flask.flask_session import FlaskSession
from workers_control.flask.forms import LoginForm
from workers_control.flask.types import Response
from workers_control.web.www.controllers.log_in_accountant_controller import (
    LogInAccountantController,
)
from workers_control.web.www.presenters.log_in_accountant_presenter import (
    LogInAccountantPresenter,
)

TEMPLATE_NAME = "auth/login_accountant.html"


@dataclass
class LogInAccountantView:
    flask_session: FlaskSession
    controller: LogInAccountantController
    interactor: LogInAccountantInteractor
    presenter: LogInAccountantPresenter

    def GET(self) -> Response:
        return self._render_or_redirect_authenticated(LoginForm(request.form))

    @commit_changes
    def POST(self) -> Response:
        form = LoginForm(request.form)
        if not form.validate():
            return self._render_or_redirect_authenticated(form)
        interactor_request = self.controller.process_login_form(form)
        interactor_response = self.interactor.log_in_accountant(interactor_request)
        view_model = self.presenter.present_login_process(
            form=form, response=interactor_response
        )
        if view_model.redirect_url is not None:
            return redirect(view_model.redirect_url)
        return FlaskResponse(render_template(TEMPLATE_NAME, form=form), status=401)

    def _render_or_redirect_authenticated(self, form: LoginForm) -> Response:
        if self.flask_session.is_current_user_authenticated():
            if self.flask_session.is_logged_in_as_accountant():
                return redirect(url_for("main_accountant.dashboard"))
            self.flask_session.logout()
        return render_template(TEMPLATE_NAME, form=form)
