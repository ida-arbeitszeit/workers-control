from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import redirect, render_template, request

from workers_control.core.interactors.request_email_address_change import (
    RequestEmailAddressChangeInteractor,
)
from workers_control.db import commit_changes
from workers_control.flask.forms import RequestEmailAddressChangeForm
from workers_control.flask.types import Response
from workers_control.web.www.controllers.request_email_address_change_controller import (
    RequestEmailAddressChangeController,
)
from workers_control.web.www.presenters.request_email_address_change_presenter import (
    RequestEmailAddressChangePresenter,
)

TEMPLATE_NAME = "user/request_email_address_change.html"


@dataclass
class RequestEmailAddressChangeView:
    controller: RequestEmailAddressChangeController
    presenter: RequestEmailAddressChangePresenter
    interactor: RequestEmailAddressChangeInteractor

    def GET(self) -> Response:
        form = RequestEmailAddressChangeForm(request.form)
        return FlaskResponse(render_template(TEMPLATE_NAME, form=form), status=200)

    @commit_changes
    def POST(self) -> Response:
        form = RequestEmailAddressChangeForm(request.form)
        if not form.validate():
            return FlaskResponse(render_template(TEMPLATE_NAME, form=form), status=400)
        uc_request = self.controller.process_email_address_change_request(form)
        uc_response = self.interactor.request_email_address_change(uc_request)
        view_model = self.presenter.render_response(uc_response, form)
        if view_model.redirect_url:
            return redirect(view_model.redirect_url)
        return FlaskResponse(render_template(TEMPLATE_NAME, form=form), status=400)
