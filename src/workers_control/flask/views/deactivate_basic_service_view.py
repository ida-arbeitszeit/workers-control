from dataclasses import dataclass
from uuid import UUID

import flask

from workers_control.core.interactors.deactivate_basic_service import (
    DeactivateBasicServiceInteractor,
)
from workers_control.db import commit_changes
from workers_control.flask.types import Response
from workers_control.web.www.controllers.deactivate_basic_service_controller import (
    DeactivateBasicServiceController,
    InvalidRequest,
)
from workers_control.web.www.presenters.deactivate_basic_service_presenter import (
    DeactivateBasicServicePresenter,
)


@dataclass
class DeactivateBasicServiceView:
    controller: DeactivateBasicServiceController
    interactor: DeactivateBasicServiceInteractor
    presenter: DeactivateBasicServicePresenter

    @commit_changes
    def POST(self, basic_service_id: UUID) -> Response:
        uc_request = self.controller.process_request(basic_service_id)
        match uc_request:
            case InvalidRequest(status_code=status_code):
                return flask.Response(status=status_code)
        response = self.interactor.execute(uc_request)
        self.presenter.present(response)
        return flask.redirect(flask.url_for("main_member.basic_services"))
