from dataclasses import dataclass

import flask

from workers_control.core.interactors.list_basic_services_of_worker import (
    ListBasicServicesOfWorkerInteractor,
)
from workers_control.flask.types import Response
from workers_control.web.www.controllers.list_basic_services_of_worker_controller import (
    InvalidRequest,
    ListBasicServicesOfWorkerController,
)
from workers_control.web.www.presenters.list_basic_services_of_worker_presenter import (
    ListBasicServicesOfWorkerPresenter,
)


@dataclass
class ListBasicServicesOfWorkerView:
    controller: ListBasicServicesOfWorkerController
    interactor: ListBasicServicesOfWorkerInteractor
    presenter: ListBasicServicesOfWorkerPresenter

    def GET(self) -> Response:
        uc_request = self.controller.process_request()
        match uc_request:
            case InvalidRequest(status_code=status_code):
                return flask.Response(status=status_code)
        response = self.interactor.list_basic_services_of_worker(uc_request)
        view_model = self.presenter.present(response)
        return flask.Response(
            flask.render_template(
                "member/basic_services.html",
                view_model=view_model,
            )
        )
