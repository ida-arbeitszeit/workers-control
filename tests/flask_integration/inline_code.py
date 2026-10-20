from html.parser import HTMLParser

from flask import Response

URL_ATTRIBUTES = {"href", "src", "action", "formaction"}


def assert_no_inline_code(response: Response) -> Response:
    if response.mimetype == "text/html" and not response.direct_passthrough:
        inline_code = find_inline_code(response.get_data(as_text=True))
        assert (
            not inline_code
        ), f"The Content Security Policy blocks this inline code: {inline_code}"
    return response


def find_inline_code(html: str) -> list[str]:
    finder = _InlineCodeFinder()
    finder.feed(html)
    finder.close()
    return finder.inline_code


class _InlineCodeFinder(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.inline_code: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if _contains_inline_code(tag, attrs):
            self.inline_code.append(self.get_starttag_text() or tag)


def _contains_inline_code(tag: str, attrs: list[tuple[str, str | None]]) -> bool:
    attribute_names = {name for name, _ in attrs}
    if tag == "style" or (tag == "script" and "src" not in attribute_names):
        return True
    return any(
        name == "style"
        or name.startswith("on")
        or (
            name in URL_ATTRIBUTES
            and (value or "").strip().lower().startswith("javascript:")
        )
        for name, value in attrs
    )
