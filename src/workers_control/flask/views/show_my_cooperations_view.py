from dataclasses import dataclass

from flask import render_template

from workers_control.core.interactors.list_coordinations_of_company import (
    ListCoordinationsOfCompanyInteractor,
    ListCoordinationsOfCompanyRequest,
)
from workers_control.core.interactors.list_my_cooperating_plans import (
    ListMyCooperatingPlansInteractor,
)
from workers_control.core.interactors.show_company_cooperations import (
    Request as ShowCompanyCooperationsRequest,
)
from workers_control.core.interactors.show_company_cooperations import (
    ShowCompanyCooperationsInteractor,
)
from workers_control.flask.flask_session import FlaskSession
from workers_control.flask.types import Response
from workers_control.web.www.presenters.show_my_cooperations_presenter import (
    ShowMyCooperationsPresenter,
)


@dataclass
class ShowMyCooperationsView:
    list_coordinations: ListCoordinationsOfCompanyInteractor
    show_company_cooperations: ShowCompanyCooperationsInteractor
    list_my_cooperating_plans: ListMyCooperatingPlansInteractor
    presenter: ShowMyCooperationsPresenter
    flask_session: FlaskSession

    def GET(self) -> Response:
        current_user = self.flask_session.get_current_user()
        assert current_user
        list_coord_response = self.list_coordinations.execute(
            ListCoordinationsOfCompanyRequest(current_user)
        )
        show_company_cooperations_response = (
            self.show_company_cooperations.show_company_cooperations(
                ShowCompanyCooperationsRequest(current_user)
            )
        )
        list_my_coop_plans_response = self.list_my_cooperating_plans.list_cooperations(
            ListMyCooperatingPlansInteractor.Request(company=current_user)
        )
        view_model = self.presenter.present(
            list_coord_response=list_coord_response,
            show_company_cooperations_response=show_company_cooperations_response,
            list_my_cooperating_plans_response=list_my_coop_plans_response,
        )
        return render_template(
            "company/my_cooperations.html",
            navbar_items=self.presenter.create_navbar_items(),
            **view_model.to_dict(),
        )
