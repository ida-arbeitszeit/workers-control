from dataclasses import dataclass

from flask import redirect

from workers_control.core.interactors.end_cooperation import EndCooperationInteractor
from workers_control.db import commit_changes
from workers_control.flask import types
from workers_control.flask.flask_request import FlaskRequest
from workers_control.flask.views.http_error_view import http_404
from workers_control.web.www.controllers.end_cooperation_controller import (
    EndCooperationController,
)
from workers_control.web.www.presenters.end_cooperation_presenter import (
    EndCooperationPresenter,
)


@dataclass
class EndCooperationView:
    interactor: EndCooperationInteractor
    controller: EndCooperationController
    presenter: EndCooperationPresenter

    @commit_changes
    def POST(self) -> types.Response:
        request = FlaskRequest()
        interactor_request = self.controller.process_request_data(request=request)
        if interactor_request is None:
            return http_404()
        interactor_response = self.interactor.execute(interactor_request)
        view_model = self.presenter.present(interactor_response, web_request=request)
        if view_model.show_404:
            return http_404()
        return redirect(view_model.redirect_url)
