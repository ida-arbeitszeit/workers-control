from dataclasses import dataclass
from uuid import UUID

from flask import render_template

from workers_control.core.interactors.show_basic_service import (
    ShowBasicServiceInteractor,
)
from workers_control.flask.types import Response
from workers_control.flask.views.http_error_view import http_404
from workers_control.web.www.controllers.show_basic_service_controller import (
    ShowBasicServiceController,
)
from workers_control.web.www.presenters.show_basic_service_presenter import (
    ShowBasicServicePresenter,
)


@dataclass
class ShowBasicServiceView:
    controller: ShowBasicServiceController
    interactor: ShowBasicServiceInteractor
    presenter: ShowBasicServicePresenter

    def GET(self, basic_service_id: UUID) -> Response:
        interactor_request = self.controller.create_request(
            basic_service_id=basic_service_id
        )
        response = self.interactor.show_basic_service(interactor_request)
        view_model = self.presenter.present(response)
        if view_model is None:
            return http_404()
        return render_template(
            "user/show_basic_service.html",
            view_model=view_model,
        )
