from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import render_template

from workers_control.core.interactors import get_member_dashboard
from workers_control.flask.flask_session import FlaskSession
from workers_control.flask.types import Response
from workers_control.web.www.presenters.get_member_dashboard_presenter import (
    GetMemberDashboardPresenter,
)


@dataclass
class MemberDashboardView:
    interactor: get_member_dashboard.GetMemberDashboardInteractor
    presenter: GetMemberDashboardPresenter
    flask_session: FlaskSession

    def GET(self) -> Response:
        current_user = self.flask_session.get_current_user()
        assert current_user
        request = get_member_dashboard.Request(member=current_user)
        response = self.interactor.get_member_dashboard(request)
        view_model = self.presenter.present(response)
        return FlaskResponse(
            render_template(
                "member/dashboard.html",
                view_model=view_model,
            )
        )
