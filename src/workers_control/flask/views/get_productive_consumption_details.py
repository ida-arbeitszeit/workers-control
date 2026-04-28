from dataclasses import dataclass
from uuid import UUID

from flask import render_template

from workers_control.core.interactors.get_productive_consumption_details import (
    GetProductiveConsumptionDetailsInteractor,
)
from workers_control.flask.types import Response
from workers_control.flask.views.http_error_view import http_404
from workers_control.web.www.controllers.get_productive_consumption_details_controller import (
    GetProductiveConsumptionDetailsController,
)
from workers_control.web.www.presenters.productive_consumption_details_presenter import (
    ProductiveConsumptionDetailsPresenter,
)


@dataclass
class GetProductiveConsumptionDetailsView:
    controller: GetProductiveConsumptionDetailsController
    interactor: GetProductiveConsumptionDetailsInteractor
    presenter: ProductiveConsumptionDetailsPresenter

    def GET(self, consumption_id: UUID) -> Response:
        interactor_request = self.controller.create_request(
            consumption_id=consumption_id
        )
        interactor_response = self.interactor.get_details(interactor_request)
        if interactor_response is None:
            return http_404()
        view_model = self.presenter.present(interactor_response)
        return render_template(
            "company/consumption_details.html", view_model=view_model
        )
