from typing import Any

from flask import has_request_context

from workers_control.core.interactors import get_user_account_details
from workers_control.core.interactors.list_available_languages import (
    ListAvailableLanguagesInteractor,
)
from workers_control.flask.dependency_injection import with_injection
from workers_control.flask.flask_session import FlaskSession
from workers_control.web.www.presenters.list_available_languages_presenter import (
    ListAvailableLanguagesPresenter,
)


@with_injection()
def add_template_variables(
    list_languages_interactor: ListAvailableLanguagesInteractor,
    list_languages_presenter: ListAvailableLanguagesPresenter,
    user_account_details_interactor: get_user_account_details.GetUserAccountDetailsInteractor,
    flask_session: FlaskSession,
) -> dict[str, Any]:
    interactor_request = list_languages_interactor.Request()
    interactor_response = list_languages_interactor.list_available_languages(
        interactor_request
    )
    view_model = list_languages_presenter.present_available_languages_list(
        interactor_response
    )
    return dict(
        languages=view_model,
        current_user_name=_get_current_user_name(
            flask_session, user_account_details_interactor
        ),
    )


def _get_current_user_name(
    flask_session: FlaskSession,
    interactor: get_user_account_details.GetUserAccountDetailsInteractor,
) -> str | None:
    # Emails are rendered with templates too, sometimes outside of requests,
    # e.g. by CLI commands.
    if not has_request_context():
        return None
    user_id = flask_session.get_current_user()
    if user_id is None:
        return None
    response = interactor.get_user_account_details(
        get_user_account_details.Request(user_id=user_id)
    )
    if response.user_info is None:
        return None
    return response.user_info.name
