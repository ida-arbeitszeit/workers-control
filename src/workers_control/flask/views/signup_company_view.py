from dataclasses import dataclass

import flask
from flask import redirect, render_template, url_for

from workers_control.core.interactors.register_company import RegisterCompany
from workers_control.db import commit_changes
from workers_control.flask.flask_request import FlaskRequest
from workers_control.flask.flask_session import FlaskSession
from workers_control.flask.types import Response
from workers_control.web.forms import RegisterForm
from workers_control.web.www.controllers.register_company_controller import (
    RegisterCompanyController,
)
from workers_control.web.www.presenters.register_company_presenter import (
    RegisterCompanyPresenter,
)
from workers_control.web.www.response import Redirect

TEMPLATE_NAME = "auth/signup_company.html"


@dataclass
class SignupCompanyView:
    register_company: RegisterCompany
    controller: RegisterCompanyController
    presenter: RegisterCompanyPresenter
    flask_session: FlaskSession

    def GET(self) -> Response:
        if self.flask_session.is_current_user_authenticated():
            if self.flask_session.is_logged_in_as_company():
                return redirect(url_for("main_company.dashboard"))
            else:
                self.flask_session.logout()
        return render_template(
            TEMPLATE_NAME, form=RegisterForm(email_value="", name_value="")
        )

    @commit_changes
    def POST(self) -> Response:
        if self.flask_session.is_current_user_authenticated():
            if self.flask_session.is_logged_in_as_company():
                return redirect(url_for("main_company.dashboard"))
            else:
                self.flask_session.logout()
        match self.controller.create_request(FlaskRequest()):
            case RegisterForm() as form:
                return self._render_form_with_errors(form)
            case RegisterCompany.Request() as interactor_request:
                pass
        response = self.register_company.register_company(interactor_request)
        match self.presenter.present_company_registration(response, FlaskRequest()):
            case Redirect(url=url):
                return redirect(url)
            case RegisterForm() as form:
                return self._render_form_with_errors(form)

    def _render_form_with_errors(self, form: RegisterForm) -> Response:
        return flask.Response(render_template(TEMPLATE_NAME, form=form), 400)
