from dataclasses import dataclass

from flask import redirect, render_template

from workers_control.flask.flask_session import FlaskSession
from workers_control.flask.types import Response
from workers_control.flask.url_index import GeneralUrlIndex
from workers_control.web.session import UserRole


@dataclass
class StartView:

    flask_session: FlaskSession
    url_index: GeneralUrlIndex

    def GET(self) -> Response:
        user_role = self.flask_session.get_user_role()
        match user_role:
            case UserRole.accountant:
                return redirect(self.url_index.get_accountant_dashboard_url())
            case UserRole.company:
                return redirect(self.url_index.get_company_dashboard_url())
            case UserRole.member:
                return redirect(self.url_index.get_member_dashboard_url())
            case _:
                return render_template("auth/start.html")
