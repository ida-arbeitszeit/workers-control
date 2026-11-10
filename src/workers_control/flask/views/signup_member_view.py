from dataclasses import dataclass

import flask
from flask import redirect, render_template, url_for

from workers_control.core.interactors.register_member import RegisterMemberInteractor
from workers_control.db import commit_changes
from workers_control.flask.flask_request import FlaskRequest
from workers_control.flask.flask_session import FlaskSession
from workers_control.flask.types import Response
from workers_control.web.forms import RegisterForm
from workers_control.web.www.controllers.register_member_controller import (
    RegisterMemberController,
)
from workers_control.web.www.presenters.register_member_presenter import (
    RegisterMemberPresenter,
)
from workers_control.web.www.response import Redirect

TEMPLATE_NAME = "auth/signup_member.html"


@dataclass
class SignupMemberView:
    register_member: RegisterMemberInteractor
    controller: RegisterMemberController
    register_member_presenter: RegisterMemberPresenter
    flask_session: FlaskSession

    def GET(self) -> Response:
        if self.flask_session.is_current_user_authenticated():
            if self.flask_session.is_logged_in_as_member():
                return redirect(url_for("main_member.dashboard"))
            else:
                self.flask_session.logout()
        return render_template(
            TEMPLATE_NAME, form=RegisterForm(email_value="", name_value="")
        )

    @commit_changes
    def POST(self) -> Response:
        if self.flask_session.is_current_user_authenticated():
            if self.flask_session.is_logged_in_as_member():
                return redirect(url_for("main_member.dashboard"))
            else:
                self.flask_session.logout()
        match self.controller.create_request(FlaskRequest()):
            case RegisterForm() as form:
                return self._render_form_with_errors(form)
            case RegisterMemberInteractor.Request() as interactor_request:
                pass
        response = self.register_member.register_member(interactor_request)
        match self.register_member_presenter.present_member_registration(
            response, FlaskRequest()
        ):
            case Redirect(url=url):
                return redirect(url)
            case RegisterForm() as form:
                return self._render_form_with_errors(form)

    def _render_form_with_errors(self, form: RegisterForm) -> Response:
        return flask.Response(render_template(TEMPLATE_NAME, form=form), 400)
