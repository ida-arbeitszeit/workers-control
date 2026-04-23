from dataclasses import dataclass

from flask import Response, render_template, request

from workers_control.core.interactors.query_basic_services import (
    QueryBasicServicesInteractor,
    QueryBasicServicesRequest,
)
from workers_control.flask.flask_request import FlaskRequest
from workers_control.flask.forms import BasicServiceSearchForm
from workers_control.web.www.controllers.query_basic_services_controller import (
    QueryBasicServicesController,
)
from workers_control.web.www.presenters.query_basic_services_presenter import (
    QueryBasicServicesPresenter,
    QueryBasicServicesViewModel,
)

TEMPLATE_NAME = "user/query_basic_services.html"


@dataclass
class QueryBasicServicesView:
    query_basic_services: QueryBasicServicesInteractor
    presenter: QueryBasicServicesPresenter
    controller: QueryBasicServicesController
    request: FlaskRequest

    def GET(self) -> Response:
        form = BasicServiceSearchForm(request.args)
        if not form.validate():
            return self._get_invalid_form_response(form=form)
        interactor_request = self.controller.import_form_data(form, self.request)
        return self._handle_interactor_request(interactor_request, form=form)

    def _get_invalid_form_response(self, form: BasicServiceSearchForm) -> Response:
        return Response(
            response=self._render_response_content(
                self.presenter.get_empty_view_model(),
                form=form,
            ),
            status=400,
        )

    def _handle_interactor_request(
        self,
        interactor_request: QueryBasicServicesRequest,
        form: BasicServiceSearchForm,
    ) -> Response:
        response = self.query_basic_services.execute(interactor_request)
        view_model = self.presenter.present(response)
        return Response(self._render_response_content(view_model, form=form))

    def _render_response_content(
        self, view_model: QueryBasicServicesViewModel, form: BasicServiceSearchForm
    ) -> str:
        return render_template(
            TEMPLATE_NAME,
            form=form,
            view_model=view_model,
        )
