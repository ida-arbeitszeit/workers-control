import re

_NON_ASCII = "\u0080-\U0010ffff"
_ATOM = rf"[a-zA-Z0-9!#$%&'*+/=?^_`{{|}}~{_NON_ASCII}-]+"
_LABEL = (
    rf"[a-zA-Z0-9{_NON_ASCII}]"
    rf"(?:[a-zA-Z0-9{_NON_ASCII}-]*[a-zA-Z0-9{_NON_ASCII}])?"
)
# smtplib re-parses the address, so anything outside this shape,
# e.g. "a<b@c.d>", can reach a different recipient.
_EMAIL_ADDRESS = re.compile(rf"{_ATOM}(?:\.{_ATOM})*@{_LABEL}(?:\.{_LABEL})+")


def is_possibly_an_email_address(text: str) -> bool:
    return (
        text.isprintable()
        and len(text.encode()) <= 254
        and _EMAIL_ADDRESS.fullmatch(text) is not None
    )
