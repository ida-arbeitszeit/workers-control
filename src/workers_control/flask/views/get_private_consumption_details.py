from dataclasses import dataclass
from uuid import UUID

from flask import render_template

from workers_control.core.interactors.get_private_consumption_details import (
    GetPrivateConsumptionDetailsInteractor,
)
from workers_control.flask.types import Response
from workers_control.flask.views.http_error_view import http_404
from workers_control.web.www.controllers.get_private_consumption_details_controller import (
    GetPrivateConsumptionDetailsController,
)
from workers_control.web.www.presenters.private_consumption_details_presenter import (
    PrivateConsumptionDetailsPresenter,
)


@dataclass
class GetPrivateConsumptionDetailsView:
    controller: GetPrivateConsumptionDetailsController
    interactor: GetPrivateConsumptionDetailsInteractor
    presenter: PrivateConsumptionDetailsPresenter

    def GET(self, consumption_id: UUID) -> Response:
        interactor_request = self.controller.create_request(
            consumption_id=consumption_id
        )
        interactor_response = self.interactor.get_details(interactor_request)
        if interactor_response is None:
            return http_404()
        view_model = self.presenter.present(interactor_response)
        return render_template("member/consumption_details.html", view_model=view_model)
