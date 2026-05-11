from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import redirect, render_template, request, url_for

from workers_control.core.interactors.log_in_member import LogInMemberInteractor
from workers_control.db import commit_changes
from workers_control.flask.flask_session import FlaskSession
from workers_control.flask.forms import LoginForm
from workers_control.flask.types import Response
from workers_control.web.www.presenters.log_in_member_presenter import (
    LogInMemberPresenter,
)

TEMPLATE_NAME = "auth/login_member.html"


@dataclass
class LogInMemberView:
    flask_session: FlaskSession
    presenter: LogInMemberPresenter
    interactor: LogInMemberInteractor

    def GET(self) -> Response:
        return self._render_or_redirect_authenticated(LoginForm(request.form))

    @commit_changes
    def POST(self) -> Response:
        form = LoginForm(request.form)
        if not form.validate():
            return self._render_or_redirect_authenticated(form)
        response = self.interactor.log_in_member(
            LogInMemberInteractor.Request(
                email=form.data["email"],
                password=form.data["password"],
            )
        )
        view_model = self.presenter.present_login_process(response, form)
        if view_model.redirect_url:
            return redirect(view_model.redirect_url)
        return FlaskResponse(render_template(TEMPLATE_NAME, form=form), status=401)

    def _render_or_redirect_authenticated(self, form: LoginForm) -> Response:
        if self.flask_session.is_current_user_authenticated():
            if self.flask_session.is_logged_in_as_member():
                return redirect(url_for("main_member.dashboard"))
            self.flask_session.logout()
        return render_template(TEMPLATE_NAME, form=form)
