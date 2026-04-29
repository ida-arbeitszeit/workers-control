from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import redirect, render_template

from workers_control.core.interactors import (
    register_productive_consumption_of_basic_service,
)
from workers_control.core.interactors.register_productive_consumption_of_basic_service import (
    RegisterProductiveConsumptionOfBasicServiceInteractor,
)
from workers_control.core.interactors.select_productive_consumption_of_basic_service import (
    SelectProductiveConsumptionOfBasicServiceInteractor,
)
from workers_control.db import commit_changes
from workers_control.flask.flask_request import FlaskRequest
from workers_control.flask.types import Response
from workers_control.web.forms import RegisterProductiveConsumptionOfBasicServiceForm
from workers_control.web.www.controllers.register_productive_consumption_of_basic_service_controller import (
    FormError,
    RegisterProductiveConsumptionOfBasicServiceController,
)
from workers_control.web.www.controllers.select_productive_consumption_of_basic_service_controller import (
    SelectProductiveConsumptionOfBasicServiceController,
)
from workers_control.web.www.presenters.register_productive_consumption_of_basic_service_presenter import (
    RegisterProductiveConsumptionOfBasicServicePresenter,
    RenderForm,
)
from workers_control.web.www.presenters.select_productive_consumption_of_basic_service_presenter import (
    SelectProductiveConsumptionOfBasicServicePresenter,
)
from workers_control.web.www.response import Redirect


@dataclass
class RegisterProductiveConsumptionOfBasicServiceView:
    register_interactor: RegisterProductiveConsumptionOfBasicServiceInteractor
    register_controller: RegisterProductiveConsumptionOfBasicServiceController
    register_presenter: RegisterProductiveConsumptionOfBasicServicePresenter
    select_controller: SelectProductiveConsumptionOfBasicServiceController
    select_interactor: SelectProductiveConsumptionOfBasicServiceInteractor
    select_presenter: SelectProductiveConsumptionOfBasicServicePresenter

    def GET(self) -> Response:
        try:
            interactor_request = self.select_controller.process_input_data(
                FlaskRequest()
            )
        except self.select_controller.InputDataError:
            return FlaskResponse(
                self._render_template(
                    form=RegisterProductiveConsumptionOfBasicServiceForm(
                        basic_service_id_value="", amount_value=""
                    )
                ),
                status=400,
            )
        interactor_response = self.select_interactor.select(interactor_request)
        view_model = self.select_presenter.render_response(interactor_response)
        form = RegisterProductiveConsumptionOfBasicServiceForm(
            basic_service_id_value=view_model.basic_service_id or "",
            amount_value=(
                str(view_model.amount) if view_model.amount is not None else ""
            ),
        )
        return FlaskResponse(
            self._render_template(form=form, view_model=view_model),
            status=view_model.status_code,
        )

    @commit_changes
    def POST(self) -> Response:
        match self.register_controller.import_form_data(FlaskRequest()):
            case FormError() as error:
                return FlaskResponse(self._render_template(error.form), status=400)
            case (
                register_productive_consumption_of_basic_service.Request() as interactor_request
            ):
                pass
        response = self.register_interactor.execute(interactor_request)
        view_model = self.register_presenter.present(response, request=FlaskRequest())
        match view_model:
            case Redirect(url):
                return redirect(url)
            case RenderForm(status_code=status_code, form=form):
                return FlaskResponse(
                    self._render_template(form=form),
                    status=status_code,
                )

    def _render_template(
        self,
        form: RegisterProductiveConsumptionOfBasicServiceForm,
        view_model: (
            SelectProductiveConsumptionOfBasicServicePresenter.ViewModel | None
        ) = None,
    ) -> str:
        return render_template(
            "company/register_productive_consumption_of_basic_service.html",
            form=form,
            view_model=view_model,
            navbar_items=self.register_presenter.create_navbar_items(),
        )
