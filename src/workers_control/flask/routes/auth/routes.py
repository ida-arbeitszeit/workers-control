from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import login_required

from workers_control.core.interactors.confirm_company import ConfirmCompanyInteractor
from workers_control.core.interactors.confirm_member import ConfirmMemberInteractor
from workers_control.db import commit_changes
from workers_control.flask.class_based_view import as_flask_view
from workers_control.flask.dependency_injection import with_injection
from workers_control.flask.flask_session import FlaskSession
from workers_control.flask.types import Response
from workers_control.flask.views.log_in_accountant_view import LogInAccountantView
from workers_control.flask.views.log_in_company_view import LogInCompanyView
from workers_control.flask.views.log_in_member_view import LogInMemberView
from workers_control.flask.views.request_password_reset_view import (
    RequestPasswordResetView,
)
from workers_control.flask.views.resend_confirmation_view import (
    ResendConfirmationCompanyView,
    ResendConfirmationMemberView,
)
from workers_control.flask.views.reset_password_view import ResetPasswordView
from workers_control.flask.views.signup_accountant_view import SignupAccountantView
from workers_control.flask.views.signup_company_view import SignupCompanyView
from workers_control.flask.views.signup_member_view import SignupMemberView
from workers_control.web.www.authentication import (
    CompanyAuthenticator,
    MemberAuthenticator,
)
from workers_control.web.www.controllers.confirm_company_controller import (
    ConfirmCompanyController,
)
from workers_control.web.www.controllers.confirm_member_controller import (
    ConfirmMemberController,
)

auth = Blueprint("auth", __name__)


@auth.route("/")
def start() -> Response:
    return render_template("auth/start.html")


@auth.route("/help")
@with_injection()
def help() -> Response:
    return render_template("auth/help.html")


@auth.route("/language=<language>")
def set_language(language: str) -> Response:
    redirection_url = request.headers.get("Referer") or url_for("auth.start")
    session["language"] = language
    return redirect(redirection_url)


@auth.route("/unconfirmed-member")
@with_injection()
@login_required
def unconfirmed_member(authenticator: MemberAuthenticator) -> Response:
    if authenticator.is_unconfirmed_member():
        return render_template("auth/unconfirmed_member.html")
    return redirect(url_for("auth.start"))


@auth.route("/signup-member", methods=["GET", "POST"])
@as_flask_view()
class signup_member(SignupMemberView): ...


@auth.route("/confirm-member/<token>")
@commit_changes
@with_injection()
def confirm_email_member(
    token: str, interactor: ConfirmMemberInteractor, controller: ConfirmMemberController
) -> Response:
    interactor_request = controller.process_request(token)
    if interactor_request is not None:
        response = interactor.confirm_member(request=interactor_request)
        if response.is_confirmed:
            return redirect(url_for("auth.login_member"))
    flash("Der Bestätigungslink ist ungültig oder ist abgelaufen.")
    return redirect(url_for("auth.unconfirmed_member"))


@auth.route("/login-member", methods=["GET", "POST"])
@as_flask_view()
class login_member(LogInMemberView): ...


@auth.route("/member/resend", methods=["POST"])
@login_required
@as_flask_view()
class resend_confirmation_member(ResendConfirmationMemberView): ...


@auth.route("/company/unconfirmed")
@with_injection()
@login_required
def unconfirmed_company(authenticator: CompanyAuthenticator) -> Response:
    if authenticator.is_unconfirmed_company():
        return render_template("auth/unconfirmed_company.html")
    return redirect(url_for("auth.start"))


@auth.route("/company/login", methods=["GET", "POST"])
@as_flask_view()
class login_company(LogInCompanyView): ...


@auth.route("/company/signup", methods=["GET", "POST"])
@as_flask_view()
class signup_company(SignupCompanyView): ...


@auth.route("/company/confirm/<token>")
@commit_changes
@with_injection()
def confirm_email_company(
    token: str,
    confirm_company_interactor: ConfirmCompanyInteractor,
    session: FlaskSession,
    controller: ConfirmCompanyController,
) -> Response:
    interactor_request = controller.process_request(token=token)
    if interactor_request:
        response = confirm_company_interactor.confirm_company(
            request=interactor_request
        )
        if response.is_confirmed:
            assert response.user_id
            session.login_company(response.user_id)
            flash("Das Konto wurde bestätigt. Danke!")
            return redirect(url_for("auth.login_company"))
    flash("Der Bestätigungslink ist ungültig oder ist abgelaufen.")
    return redirect(url_for("auth.unconfirmed_company"))


@auth.route("/company/resend", methods=["POST"])
@login_required
@as_flask_view()
class resend_confirmation_company(ResendConfirmationCompanyView): ...


@auth.route("/accountant/signup/<token>", methods=["GET", "POST"])
@as_flask_view()
class signup_accountant(SignupAccountantView): ...


@auth.route("/accountant/login", methods=["GET", "POST"])
@as_flask_view()
class login_accountant(LogInAccountantView): ...


@auth.route("/logout")
@with_injection()
@login_required
def logout(flask_session: FlaskSession) -> Response:
    flask_session.logout()
    return redirect(url_for("auth.start"))


@auth.route("/request-password-reset", methods=["GET", "POST"])
@as_flask_view()
class request_password_reset(RequestPasswordResetView): ...


@auth.route("/reset-password/<token>", methods=["GET", "POST"])
@as_flask_view()
class reset_password(ResetPasswordView): ...
