from dataclasses import dataclass

from flask import redirect, render_template, request

from workers_control.core.interactors.request_user_password_reset import (
    RequestUserPasswordResetInteractor,
)
from workers_control.db import commit_changes
from workers_control.flask import types
from workers_control.flask.forms import RequestPasswordResetForm
from workers_control.web.www.controllers.request_password_reset_controller import (
    RequestPasswordResetController,
)
from workers_control.web.www.presenters.request_password_reset_presenter import (
    RequestPasswordResetPresenter,
)


@dataclass
class RequestPasswordResetView:
    controller: RequestPasswordResetController
    interactor: RequestUserPasswordResetInteractor
    presenter: RequestPasswordResetPresenter

    def GET(self) -> types.Response:
        form = RequestPasswordResetForm(request.form)
        return render_template("auth/request_password_reset.html", form=form)

    @commit_changes
    def POST(self) -> types.Response:
        form = RequestPasswordResetForm(request.form)
        if form.validate():
            email = form.data["email"]
            uc_request = self.controller.create_password_reset_request(email)
            if uc_request is not None:
                self.interactor.reset_user_password(uc_request)
            view_model = self.presenter.present_password_reset_request()
            return redirect(view_model.redirect_url)
        return render_template("auth/request_password_reset.html", form=form)
