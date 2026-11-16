from dataclasses import dataclass
from workers_control.flask.types import Response
from workers_control.flask import flask_session
from workers_control.flask.url_index import GeneralUrlIndex 
from flask import redirect, render_template

@dataclass
class StartView:

    flask_session: flask_session.FlaskSession
    url_index: GeneralUrlIndex

    def GET(self) -> Response:
        user_role = self.flask_session.get_user_role()
        match user_role:
            case flask_session.UserRole.accountant:
                return redirect(self.url_index.get_accountant_dashboard_url(),302)
            case flask_session.UserRole.company:
                return redirect(self.url_index.get_company_dashboard_url(),302)
            case flask_session.UserRole.member:
                return redirect(self.url_index.get_member_dashboard_url(),302)
            case _:
                return render_template("auth/start.html")
        