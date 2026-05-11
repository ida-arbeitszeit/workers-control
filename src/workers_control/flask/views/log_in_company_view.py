from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import redirect, render_template, request, url_for

from workers_control.core.interactors.log_in_company import LogInCompanyInteractor
from workers_control.db import commit_changes
from workers_control.flask.flask_session import FlaskSession
from workers_control.flask.forms import LoginForm
from workers_control.flask.types import Response
from workers_control.web.www.presenters.log_in_company_presenter import (
    LogInCompanyPresenter,
)

TEMPLATE_NAME = "auth/login_company.html"


@dataclass
class LogInCompanyView:
    flask_session: FlaskSession
    presenter: LogInCompanyPresenter
    interactor: LogInCompanyInteractor

    def GET(self) -> Response:
        return self._render_or_redirect_authenticated(LoginForm(request.form))

    @commit_changes
    def POST(self) -> Response:
        form = LoginForm(request.form)
        if not form.validate():
            return self._render_or_redirect_authenticated(form)
        response = self.interactor.log_in_company(
            LogInCompanyInteractor.Request(
                email_address=form.data["email"],
                password=form.data["password"],
            )
        )
        view_model = self.presenter.present_login_process(
            response=response,
            form=form,
        )
        if view_model.redirect_url:
            return redirect(view_model.redirect_url)
        return FlaskResponse(render_template(TEMPLATE_NAME, form=form), status=401)

    def _render_or_redirect_authenticated(self, form: LoginForm) -> Response:
        if self.flask_session.is_current_user_authenticated():
            if self.flask_session.is_logged_in_as_company():
                return redirect(url_for("main_company.dashboard"))
            self.flask_session.logout()
        return render_template(TEMPLATE_NAME, form=form)
