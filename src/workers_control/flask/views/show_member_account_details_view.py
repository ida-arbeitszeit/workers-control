from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import render_template

from workers_control.core.interactors.show_member_account_details import (
    ShowMemberAccountDetailsInteractor,
)
from workers_control.flask.flask_session import FlaskSession
from workers_control.flask.types import Response
from workers_control.web.www.presenters.show_member_account_details_presenter import (
    ShowMemberAccountDetailsPresenter,
)


@dataclass
class ShowMemberAccountDetailsView:
    show_member_account_details: ShowMemberAccountDetailsInteractor
    presenter: ShowMemberAccountDetailsPresenter
    flask_session: FlaskSession

    def GET(self) -> Response:
        current_user = self.flask_session.get_current_user()
        assert current_user
        response = self.show_member_account_details.execute(current_user)
        view_model = self.presenter.present_member_account(response)
        return FlaskResponse(
            render_template(
                "member/my_account.html",
                view_model=view_model,
            )
        )
