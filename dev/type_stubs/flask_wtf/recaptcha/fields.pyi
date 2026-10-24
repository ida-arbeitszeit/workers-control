from _typeshed import Incomplete
from wtforms.fields import Field

__all__ = ["RecaptchaField"]

class RecaptchaField(Field):
    widget: Incomplete
    recaptcha_error: Incomplete
    nonce: Incomplete
    def __init__(
        self, label: str = "", validators=None, nonce=None, **kwargs
    ) -> None: ...
