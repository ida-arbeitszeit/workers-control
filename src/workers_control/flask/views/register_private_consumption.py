from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import redirect, render_template, request

from workers_control.core.interactors.register_private_consumption import (
    RegisterPrivateConsumption,
    RegisterPrivateConsumptionRequest,
)
from workers_control.db import commit_changes
from workers_control.flask.flask_request import FlaskRequest
from workers_control.flask.flask_session import FlaskSession
from workers_control.flask.types import Response
from workers_control.web.forms import RegisterPrivateConsumptionForm
from workers_control.web.www.controllers.register_private_consumption_controller import (
    FormError,
    RegisterPrivateConsumptionController,
)
from workers_control.web.www.presenters.register_private_consumption_presenter import (
    RegisterPrivateConsumptionPresenter,
    RenderForm,
)
from workers_control.web.www.response import Redirect


@dataclass
class RegisterPrivateConsumptionView:
    flask_session: FlaskSession
    register_private_consumption: RegisterPrivateConsumption
    controller: RegisterPrivateConsumptionController
    presenter: RegisterPrivateConsumptionPresenter

    def GET(self) -> Response:
        form = RegisterPrivateConsumptionForm(
            amount_value=request.args.get("amount") or "",
            plan_id_value=request.args.get("plan_id") or "",
        )
        return FlaskResponse(self._render_template(form=form))

    @commit_changes
    def POST(self) -> Response:
        match self.controller.import_form_data(FlaskRequest()):
            case FormError() as error:
                return FlaskResponse(self._render_template(error.form), status=400)
            case Redirect(url=url):
                return redirect(url)
            case RegisterPrivateConsumptionRequest() as interactor_request:
                pass
        response = self.register_private_consumption.register_private_consumption(
            interactor_request
        )
        view_model = self.presenter.present(response, request=FlaskRequest())
        match view_model:
            case Redirect(url):
                return redirect(url)
            case RenderForm(status_code=status_code, form=form):
                return FlaskResponse(
                    render_template(
                        "member/register_private_consumption.html", form=form
                    ),
                    status=status_code,
                )

    def _render_template(self, form: RegisterPrivateConsumptionForm) -> str:
        return render_template("member/register_private_consumption.html", form=form)
