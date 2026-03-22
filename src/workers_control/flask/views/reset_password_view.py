from dataclasses import dataclass

from flask import redirect, render_template, request

from workers_control.core.interactors.change_user_password import (
    ChangeUserPasswordInteractor,
)
from workers_control.db import commit_changes
from workers_control.flask import types
from workers_control.flask.forms import ResetPasswordForm
from workers_control.web.www.controllers.reset_password_controller import (
    ResetPasswordController,
)
from workers_control.web.www.presenters.reset_password_presenter import (
    ResetPasswordPresenter,
)


@dataclass
class ResetPasswordView:
    controller: ResetPasswordController
    interactor: ChangeUserPasswordInteractor
    presenter: ResetPasswordPresenter

    def GET(self, token: str) -> types.Response:
        email = self.controller.validate_token(token)
        if email is None:
            return render_template("auth/reset_password_invalid.html")
        form = ResetPasswordForm()
        return render_template("auth/reset_password.html", form=form)

    @commit_changes
    def POST(self, token: str) -> types.Response:
        form = ResetPasswordForm(request.form)
        if form.validate():
            uc_request = self.controller.create_request(token, form.data["password"])
            if uc_request is None:
                return render_template("auth/reset_password_invalid.html")
            response = self.interactor.change_user_password(uc_request)
            view_model = self.presenter.present_password_change(response)
            assert view_model.redirect_url
            return redirect(view_model.redirect_url)
        return render_template("auth/reset_password.html", form=form)
