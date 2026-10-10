from functools import wraps
from typing import Any, Callable, TypeVar, cast

from flask import redirect

from workers_control.flask.dependency_injection import create_dependency_injector
from workers_control.web.notification import Notifier
from workers_control.web.session import Session
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex

ViewFunction = TypeVar("ViewFunction", bound=Callable[..., Any])


def login_required(view_function: ViewFunction) -> ViewFunction:
    @wraps(view_function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        injector = create_dependency_injector()
        if injector.get(Session).get_current_user() is None:
            translator = injector.get(Translator)
            injector.get(Notifier).display_warning(
                translator.gettext("Please log in to view this page.")
            )
            return redirect(injector.get(UrlIndex).get_start_page_url())
        return view_function(*args, **kwargs)

    return cast(ViewFunction, wrapper)
