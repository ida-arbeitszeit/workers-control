from functools import wraps
from typing import Any, Callable

from flask import request

from workers_control.flask.dependency_injection import create_dependency_injector
from workers_control.flask.types import Response
from workers_control.flask.views.http_error_view import http_501


def _not_implemented_view(*args: Any, **kwargs: Any) -> Response:
    return http_501()


class as_flask_view:
    def __call__(self, view_class: type[Any]) -> Callable[..., Response]:
        @wraps(view_class)
        def wrapper(*args: Any, **kwargs: Any) -> Response:
            injector = create_dependency_injector()
            view = injector.get(view_class)
            dispatched_method = getattr(view, request.method, _not_implemented_view)
            return dispatched_method(*args, **kwargs)

        return wrapper
