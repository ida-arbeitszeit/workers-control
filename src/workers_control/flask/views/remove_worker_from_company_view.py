from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import redirect, render_template

from workers_control.core.interactors.list_workers import ListWorkersInteractor
from workers_control.core.interactors.remove_worker_from_company import (
    RemoveWorkerFromCompanyInteractor,
)
from workers_control.db import commit_changes
from workers_control.db.db import Database
from workers_control.flask.flask_request import FlaskRequest
from workers_control.flask.flask_session import FlaskSession
from workers_control.flask.types import Response
from workers_control.web.www.controllers.list_workers_controller import (
    ListWorkersController,
)
from workers_control.web.www.controllers.remove_worker_from_company_controller import (
    RemoveWorkerFromCompanyController,
)
from workers_control.web.www.presenters.list_workers_presenter import (
    ListWorkersPresenter,
)
from workers_control.web.www.presenters.remove_worker_from_company_presenter import (
    RemoveWorkerFromCompanyPresenter,
)
from workers_control.web.www.response import Redirect

TEMPLATE_NAME = "company/remove_worker_from_company.html"


@dataclass
class RemoveWorkerFromCompanyView:
    list_workers_controller: ListWorkersController
    list_workers_interactor: ListWorkersInteractor
    list_workers_presenter: ListWorkersPresenter
    remove_worker_controller: RemoveWorkerFromCompanyController
    remove_worker_interactor: RemoveWorkerFromCompanyInteractor
    remove_worker_presenter: RemoveWorkerFromCompanyPresenter

    def GET(self) -> Response:
        return self.list_workers_response(200)

    @commit_changes
    def POST(self) -> Response:
        web_request = FlaskRequest()
        session = FlaskSession(Database())
        interactor_request = self.remove_worker_controller.create_interactor_request(
            web_request=web_request, session=session
        )
        if not interactor_request:
            return self.list_workers_response(400)
        interactor_response = self.remove_worker_interactor.remove_worker_from_company(
            interactor_request
        )
        view_model = self.remove_worker_presenter.present(interactor_response)
        if isinstance(view_model, Redirect):
            return redirect(view_model.url)
        return self.list_workers_response(view_model.code)

    def list_workers_response(self, status_code: int) -> Response:
        list_workers_interactor_request = (
            self.list_workers_controller.create_interactor_request()
        )
        list_workers_interactor_response = self.list_workers_interactor.execute(
            list_workers_interactor_request
        )
        list_workers_view_model = self.list_workers_presenter.show_workers_list(
            list_workers_interactor_response
        )
        return FlaskResponse(
            render_template(TEMPLATE_NAME, workers=list_workers_view_model.workers),
            status=status_code,
        )
