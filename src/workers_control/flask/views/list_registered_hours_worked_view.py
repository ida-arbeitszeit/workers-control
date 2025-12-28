from dataclasses import dataclass

import flask

from workers_control.core.interactors.list_registered_hours_worked import (
    ListRegisteredHoursWorkedInteractor,
)
from workers_control.flask import types
from workers_control.web.www.controllers.list_registered_hours_worked_controller import (
    ListRegisteredHoursWorkedController,
)
from workers_control.web.www.presenters.list_registered_hours_worked_presenter import (
    ListRegisteredHoursWorkedPresenter,
)


@dataclass
class ListRegisteredHoursWorkedView:
    controller: ListRegisteredHoursWorkedController
    interactor: ListRegisteredHoursWorkedInteractor
    presenter: ListRegisteredHoursWorkedPresenter

    def GET(self) -> types.Response:
        request = self.controller.create_request()
        response = self.interactor.list_registered_hours_worked(request)
        view_model = self.presenter.present(response)
        return flask.Response(
            flask.render_template(
                "company/list_registered_hours_worked.html",
                view_model=view_model,
            )
        )
