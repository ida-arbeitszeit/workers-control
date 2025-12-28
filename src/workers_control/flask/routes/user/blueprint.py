from functools import wraps
from typing import Callable, TypeVar

from flask import Blueprint, redirect, request

from workers_control.flask import types
from workers_control.flask.dependency_injection import create_dependency_injector
from workers_control.flask.views.http_error_view import http_403
from workers_control.web.www.authentication import UserAuthenticator

ViewFunction = TypeVar("ViewFunction", bound=Callable)

user_blueprint = Blueprint("main_user", __name__)


class AuthenticatedUserRoute:
    def __init__(self, route_string: str, methods: list[str] | None = None) -> None:
        self.route_string = route_string
        self.methods = methods or ["GET"]

    def __call__(self, view_function: ViewFunction) -> ViewFunction:
        @wraps(view_function)
        def wrapper(*args, **kwargs) -> types.Response:
            injector = create_dependency_injector()
            authenticator = injector.get(UserAuthenticator)
            if not authenticator.is_user_authenticated():
                if request.method == "GET":
                    # Security: FlaskSession has a check implemented when we
                    # set_next_url.
                    redirect_url = authenticator.redirect_user_to_start_page()
                    return redirect(redirect_url)
                else:
                    return http_403()
            return injector.call_with_injection(
                view_function,
                args=args,
                kwargs=kwargs,
            )

        user_blueprint.route(self.route_string, methods=self.methods)(wrapper)
        # We return the original view_function to mimic the behavior
        # of flask itself in this regard. The flask @route decorator
        # also returns the original function that was passed into it.
        return view_function
