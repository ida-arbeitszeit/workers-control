from dataclasses import dataclass

import flask
from flask import redirect, render_template, request, url_for

from workers_control.core.interactors.register_company import RegisterCompany
from workers_control.db import commit_changes
from workers_control.flask.flask_session import FlaskSession
from workers_control.flask.forms import RegisterForm
from workers_control.flask.types import Response
from workers_control.web.www.controllers.register_company_controller import (
    RegisterCompanyController,
)
from workers_control.web.www.presenters.register_company_presenter import (
    RegisterCompanyPresenter,
)


@dataclass
class SignupCompanyView:
    register_company: RegisterCompany
    controller: RegisterCompanyController
    presenter: RegisterCompanyPresenter
    flask_session: FlaskSession

    def GET(self) -> Response:
        register_form = RegisterForm(request.form)
        if self.flask_session.is_current_user_authenticated():
            if self.flask_session.is_logged_in_as_company():
                return redirect(url_for("main_company.dashboard"))
            else:
                self.flask_session.logout()
        return render_template("auth/signup_company.html", form=register_form)

    @commit_changes
    def POST(self) -> Response:
        register_form = RegisterForm(request.form)
        if register_form.validate():
            return self._handle_successful_post_request(register_form)
        if self.flask_session.is_current_user_authenticated():
            if self.flask_session.is_logged_in_as_company():
                return redirect(url_for("main_company.dashboard"))
            else:
                self.flask_session.logout()
        return flask.Response(
            render_template("auth/signup_company.html", form=register_form), 400
        )

    def _handle_successful_post_request(self, register_form: RegisterForm) -> Response:
        interactor_request = self.controller.create_request(register_form)
        response = self.register_company.register_company(interactor_request)
        view_model = self.presenter.present_company_registration(
            response=response, form=register_form
        )
        if view_model.is_success_view:
            return redirect(url_for("auth.unconfirmed_company"))
        return render_template("auth/signup_company.html", form=register_form)
