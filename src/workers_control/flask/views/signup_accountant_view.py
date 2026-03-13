from dataclasses import dataclass

from flask import Response, redirect, render_template, request

from workers_control.core.interactors.register_accountant import (
    RegisterAccountantInteractor,
)
from workers_control.db import commit_changes
from workers_control.flask import types
from workers_control.flask.forms import RegisterAccountantForm
from workers_control.web.www.controllers.register_accountant_controller import (
    RegisterAccountantController,
)
from workers_control.web.www.presenters.register_accountant_presenter import (
    RegisterAccountantPresenter,
)


@dataclass
class SignupAccountantView:
    controller: RegisterAccountantController
    presenter: RegisterAccountantPresenter
    interactor: RegisterAccountantInteractor

    def GET(self, token: str) -> types.Response:
        return Response(
            response=render_template(
                "auth/signup_accountant.html",
                form=RegisterAccountantForm(),
            ),
            status=200,
        )

    @commit_changes
    def POST(self, token: str) -> types.Response:
        form = RegisterAccountantForm(request.form)
        result = self.controller.create_interactor_request(form=form, token=token)
        if result is None:
            view_model = self.presenter.present_registration_result(None)
            assert view_model.redirect_url
            return redirect(view_model.redirect_url)
        form.extracted_token = result.token_email
        if form.validate():
            interactor_response = self.interactor.register_accountant(result.request)
            view_model = self.presenter.present_registration_result(interactor_response)
            if view_model.redirect_url:
                return redirect(view_model.redirect_url)
        return Response(
            response=render_template(
                "auth/signup_accountant.html",
                form=form,
            ),
            status=400,
        )
