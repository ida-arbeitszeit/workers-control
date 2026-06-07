from dataclasses import dataclass

from flask import render_template

from workers_control.core.interactors.show_my_plans import (
    ShowMyPlansInteractor,
    ShowMyPlansRequest,
)
from workers_control.flask.flask_session import FlaskSession
from workers_control.flask.types import Response
from workers_control.web.www.presenters.show_my_plans_presenter import (
    ShowMyPlansPresenter,
)


@dataclass
class ShowMyPlansView:
    show_my_plans_interactor: ShowMyPlansInteractor
    show_my_plans_presenter: ShowMyPlansPresenter
    flask_session: FlaskSession

    def GET(self) -> Response:
        current_user = self.flask_session.get_current_user()
        assert current_user
        request = ShowMyPlansRequest(company_id=current_user)
        response = self.show_my_plans_interactor.show_company_plans(request)
        view_model = self.show_my_plans_presenter.present(response)
        return render_template(
            "company/my_plans.html",
            navbar_items=self.show_my_plans_presenter.create_navbar_items(),
            **view_model.to_dict(),
        )
