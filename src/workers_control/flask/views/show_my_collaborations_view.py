from dataclasses import dataclass

from flask import render_template

from workers_control.core.interactors.list_coordinations_of_company import (
    ListCoordinationsOfCompanyInteractor,
    ListCoordinationsOfCompanyRequest,
)
from workers_control.core.interactors.list_my_collaborating_plans import (
    ListMyCollaboratingPlansInteractor,
)
from workers_control.core.interactors.show_company_collaborations import (
    Request as ShowCompanyCollaborationsRequest,
)
from workers_control.core.interactors.show_company_collaborations import (
    ShowCompanyCollaborationsInteractor,
)
from workers_control.flask.flask_session import FlaskSession
from workers_control.flask.types import Response
from workers_control.web.www.presenters.show_my_collaborations_presenter import (
    ShowMyCollaborationsPresenter,
)


@dataclass
class ShowMyCollaborationsView:
    list_coordinations: ListCoordinationsOfCompanyInteractor
    show_company_collaborations: ShowCompanyCollaborationsInteractor
    list_my_collaborating_plans: ListMyCollaboratingPlansInteractor
    presenter: ShowMyCollaborationsPresenter
    flask_session: FlaskSession

    def GET(self) -> Response:
        current_user = self.flask_session.get_current_user()
        assert current_user
        list_coord_response = self.list_coordinations.execute(
            ListCoordinationsOfCompanyRequest(current_user)
        )
        show_company_collaborations_response = (
            self.show_company_collaborations.show_company_collaborations(
                ShowCompanyCollaborationsRequest(current_user)
            )
        )
        list_my_collab_plans_response = (
            self.list_my_collaborating_plans.list_collaborations(
                ListMyCollaboratingPlansInteractor.Request(company=current_user)
            )
        )
        view_model = self.presenter.present(
            list_coord_response=list_coord_response,
            show_company_collaborations_response=show_company_collaborations_response,
            list_my_collaborating_plans_response=list_my_collab_plans_response,
        )
        return render_template(
            "company/my_collaborations.html",
            navbar_items=self.presenter.create_navbar_items(),
            **view_model.to_dict(),
        )
