from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import redirect, render_template, request

from workers_control.core.interactors.register_productive_consumption import (
    RegisterProductiveConsumptionInteractor,
)
from workers_control.core.interactors.select_productive_consumption import (
    SelectProductiveConsumptionInteractor,
)
from workers_control.db import commit_changes
from workers_control.flask.flask_request import FlaskRequest
from workers_control.flask.forms import RegisterProductiveConsumptionForm
from workers_control.flask.types import Response
from workers_control.web.www.controllers.register_productive_consumption_controller import (
    RegisterProductiveConsumptionController,
)
from workers_control.web.www.controllers.select_productive_consumption_controller import (
    SelectProductiveConsumptionController,
)
from workers_control.web.www.presenters.register_productive_consumption_presenter import (
    RegisterProductiveConsumptionPresenter,
)
from workers_control.web.www.presenters.select_productive_consumption_presenter import (
    SelectProductiveConsumptionPresenter,
)


@dataclass
class RegisterProductiveConsumptionView:
    select_productive_consumption_controller: SelectProductiveConsumptionController
    select_productive_consumption_interactor: SelectProductiveConsumptionInteractor
    select_productive_consumption_presenter: SelectProductiveConsumptionPresenter
    controller: RegisterProductiveConsumptionController
    register_productive_consumption: RegisterProductiveConsumptionInteractor
    presenter: RegisterProductiveConsumptionPresenter

    def GET(self) -> Response:
        try:
            interactor_request = (
                self.select_productive_consumption_controller.process_input_data(
                    FlaskRequest()
                )
            )
        except self.select_productive_consumption_controller.InputDataError:
            return self._handle_invalid_form(RegisterProductiveConsumptionForm())
        interactor_response = (
            self.select_productive_consumption_interactor.select_productive_consumption(
                interactor_request
            )
        )
        view_model = self.select_productive_consumption_presenter.render_response(
            interactor_response
        )
        form = RegisterProductiveConsumptionForm(
            plan_id=view_model.plan_id,
            amount=view_model.amount,
            type_of_consumption=(
                "fixed" if view_model.is_consumption_of_fixed_means else "liquid"
            ),
        )
        return FlaskResponse(
            render_template(
                "company/register_productive_consumption.html",
                form=form,
                view_model=view_model,
            ),
            status=view_model.status_code,
        )

    @commit_changes
    def POST(self) -> Response:
        form = RegisterProductiveConsumptionForm(request.form)
        if not form.validate():
            return self._handle_invalid_form(form)
        try:
            data = self.controller.process_input_data(form)
        except self.controller.FormError:
            return self._handle_invalid_form(form)
        interactor_response = self.register_productive_consumption.execute(data)
        view_model = self.presenter.present(interactor_response)
        if view_model.redirect_url:
            return redirect(view_model.redirect_url)
        return FlaskResponse(self._render_template(form), status=400)

    def _render_template(self, form: RegisterProductiveConsumptionForm) -> str:
        return render_template(
            "company/register_productive_consumption.html", form=form, view_model=None
        )

    def _handle_invalid_form(self, form: RegisterProductiveConsumptionForm) -> Response:
        return FlaskResponse(self._render_template(form), status=400)
