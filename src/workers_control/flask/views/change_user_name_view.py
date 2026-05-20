from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import redirect, render_template, request

from workers_control.core.interactors.change_user_name import (
    ChangeUserNameInteractor,
)
from workers_control.db import commit_changes
from workers_control.flask.forms import ChangeUserNameForm
from workers_control.flask.types import Response
from workers_control.web.www.controllers.change_user_name_controller import (
    ChangeUserNameController,
)
from workers_control.web.www.presenters.change_user_name_presenter import (
    ChangeUserNamePresenter,
)

TEMPLATE_NAME = "user/change_user_name.html"


@dataclass
class ChangeUserNameView:
    controller: ChangeUserNameController
    presenter: ChangeUserNamePresenter
    interactor: ChangeUserNameInteractor

    def GET(self) -> Response:
        form = ChangeUserNameForm(request.form)
        return FlaskResponse(render_template(TEMPLATE_NAME, form=form), status=200)

    @commit_changes
    def POST(self) -> Response:
        form = ChangeUserNameForm(request.form)
        if not form.validate():
            return FlaskResponse(render_template(TEMPLATE_NAME, form=form), status=400)
        uc_request = self.controller.process_change_user_name_request(form)
        uc_response = self.interactor.change_user_name(uc_request)
        view_model = self.presenter.render_response(uc_response, form)
        if view_model.redirect_url:
            return redirect(view_model.redirect_url)
        return FlaskResponse(render_template(TEMPLATE_NAME, form=form), status=400)
