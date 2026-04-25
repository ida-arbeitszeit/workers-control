from dataclasses import dataclass

from flask import Response, render_template, request

from workers_control.core.interactors import query_offers as interactor
from workers_control.flask.flask_request import FlaskRequest
from workers_control.flask.forms import OfferSearchForm
from workers_control.web.www.controllers.query_offers_controller import (
    QueryOffersController,
)
from workers_control.web.www.presenters.query_offers_presenter import (
    QueryOffersPresenter,
    QueryOffersViewModel,
)

TEMPLATE_NAME = "user/query_offers.html"


@dataclass
class QueryOffersView:
    query_offers: interactor.QueryOffersInteractor
    presenter: QueryOffersPresenter
    controller: QueryOffersController
    request: FlaskRequest

    def GET(self) -> Response:
        form = OfferSearchForm(request.args)
        if not form.validate():
            return self._get_invalid_form_response(form=form)
        interactor_request = self.controller.import_form_data(form, self.request)
        return self._handle_interactor_request(interactor_request, form=form)

    def _get_invalid_form_response(self, form: OfferSearchForm) -> Response:
        return Response(
            response=self._render_response_content(
                self.presenter.get_empty_view_model(),
                form=form,
            ),
            status=400,
        )

    def _handle_interactor_request(
        self,
        interactor_request: interactor.QueryOffersRequest,
        form: OfferSearchForm,
    ) -> Response:
        response = self.query_offers.execute(interactor_request)
        view_model = self.presenter.present(response)
        return Response(self._render_response_content(view_model, form=form))

    def _render_response_content(
        self, view_model: QueryOffersViewModel, form: OfferSearchForm
    ) -> str:
        return render_template(
            TEMPLATE_NAME,
            form=form,
            view_model=view_model,
        )
