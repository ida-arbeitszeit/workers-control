from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import redirect, render_template, request, url_for

from workers_control.core.interactors.create_basic_service import (
    CreateBasicServiceInteractor,
)
from workers_control.db import commit_changes
from workers_control.flask.forms import CreateBasicServiceForm
from workers_control.flask.types import Response
from workers_control.web.www.controllers.create_basic_service_controller import (
    CreateBasicServiceController,
    InvalidRequest,
)
from workers_control.web.www.presenters.create_basic_service_presenter import (
    CreateBasicServicePresenter,
)


@dataclass
class CreateBasicServiceView:
    interactor: CreateBasicServiceInteractor
    presenter: CreateBasicServicePresenter
    controller: CreateBasicServiceController

    def GET(self) -> Response:
        return FlaskResponse(
            self._render_template(CreateBasicServiceForm()), status=200
        )

    @commit_changes
    def POST(self) -> Response:
        form = CreateBasicServiceForm(request.form)
        if not form.validate():
            return FlaskResponse(self._render_template(form), status=400)
        match self.controller.import_form_data(form):
            case InvalidRequest(status_code=status_code):
                return FlaskResponse(self._render_template(form), status=status_code)
            case interactor_request:
                pass
        interactor_response = self.interactor.execute(interactor_request)
        self.presenter.present(interactor_response)
        if interactor_response.is_rejected:
            return FlaskResponse(self._render_template(form), status=400)
        return redirect(url_for("main_member.basic_services"))

    def _render_template(self, form: CreateBasicServiceForm) -> str:
        return render_template("member/create_basic_service.html", form=form)
