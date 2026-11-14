from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import render_template

from workers_control.core.interactors.query_company_consumptions import (
    QueryCompanyConsumptionsInteractor,
)
from workers_control.flask.flask_session import FlaskSession
from workers_control.flask.types import Response
from workers_control.web.www.presenters.company_consumptions_presenter import (
    CompanyConsumptionsPresenter,
)


@dataclass
class QueryCompanyConsumptionsView:
    query_consumptions: QueryCompanyConsumptionsInteractor
    presenter: CompanyConsumptionsPresenter
    flask_session: FlaskSession

    def GET(self) -> Response:
        current_user = self.flask_session.get_current_user()
        assert current_user
        response = self.query_consumptions.execute(current_user)
        view_model = self.presenter.present(response)
        return FlaskResponse(
            render_template(
                "company/my_consumptions.html",
                view_model=view_model,
            )
        )
