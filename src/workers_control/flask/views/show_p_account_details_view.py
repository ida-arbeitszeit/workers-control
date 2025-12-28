from dataclasses import dataclass
from uuid import UUID

from flask import Response, render_template

from workers_control.core.interactors.show_p_account_details import (
    ShowPAccountDetailsInteractor,
)
from workers_control.web.www.controllers.show_p_account_details_controller import (
    ShowPAccountDetailsController,
)
from workers_control.web.www.presenters.show_p_account_details_presenter import (
    ShowPAccountDetailsPresenter,
)


@dataclass
class ShowPAccountDetailsView:
    controller: ShowPAccountDetailsController
    interactor: ShowPAccountDetailsInteractor
    presenter: ShowPAccountDetailsPresenter

    def GET(self, company_id: UUID) -> Response:
        interactor_request = self.controller.create_request(company=company_id)
        response = self.interactor.show_details(interactor_request)
        view_model = self.presenter.present(response)
        return Response(
            render_template(
                "user/company_account_p.html",
                view_model=view_model,
            )
        )
