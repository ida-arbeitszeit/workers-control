from dataclasses import dataclass
from typing import ClassVar

from flask import flash, redirect, url_for

from workers_control.core.interactors.resend_confirmation_mail import (
    ResendConfirmationMailInteractor,
)
from workers_control.db import commit_changes
from workers_control.flask.flask_session import FlaskSession
from workers_control.flask.types import Response


@dataclass
class _ResendConfirmationView:
    interactor: ResendConfirmationMailInteractor
    session: FlaskSession

    redirect_endpoint: ClassVar[str]

    @commit_changes
    def POST(self) -> Response:
        current_user = self.session.get_current_user()
        assert current_user
        response = self.interactor.resend_confirmation_mail(
            self.interactor.Request(user=current_user)
        )
        if response.is_token_sent:
            flash("Eine neue Bestätigungsmail wurde gesendet.")
        else:
            flash("Bestätigungsmail konnte nicht gesendet werden!")
        return redirect(url_for(self.redirect_endpoint))


class ResendConfirmationMemberView(_ResendConfirmationView):
    redirect_endpoint = "auth.unconfirmed_member"


class ResendConfirmationCompanyView(_ResendConfirmationView):
    redirect_endpoint = "auth.unconfirmed_company"
