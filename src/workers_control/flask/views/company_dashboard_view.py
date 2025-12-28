from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import render_template

from workers_control.core.interactors.get_company_dashboard import (
    GetCompanyDashboardInteractor,
)
from workers_control.flask.flask_session import FlaskSession
from workers_control.flask.types import Response
from workers_control.flask.views.http_error_view import http_404
from workers_control.web.www.presenters.get_company_dashboard_presenter import (
    GetCompanyDashboardPresenter,
)


@dataclass
class CompanyDashboardView:
    get_company_dashboard_interactor: GetCompanyDashboardInteractor
    get_company_dashboard_presenter: GetCompanyDashboardPresenter
    flask_session: FlaskSession

    def GET(self) -> Response:
        current_user = self.flask_session.get_current_user()
        assert current_user
        try:
            response = self.get_company_dashboard_interactor.get_dashboard(current_user)
        except GetCompanyDashboardInteractor.Failure:
            return http_404()
        view_model = self.get_company_dashboard_presenter.present(response)
        return FlaskResponse(
            render_template(
                "company/dashboard.html",
                view_model=view_model,
            )
        )
