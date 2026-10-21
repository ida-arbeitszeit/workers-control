from unittest import TestCase

from tests.flask_integration.inline_code import find_inline_code


class FindInlineCodeTests(TestCase):
    def test_external_script_and_plain_markup_are_allowed(self) -> None:
        html = '<script src="/static/main.js"></script><a href="/home" class="x">a</a>'
        assert not find_inline_code(html)

    def test_inline_script_is_found(self) -> None:
        assert find_inline_code("<script>alert(1)</script>") == ["<script>"]

    def test_style_element_is_found(self) -> None:
        assert find_inline_code("<style>p {}</style>") == ["<style>"]

    def test_event_handler_attribute_is_found(self) -> None:
        html = '<span onclick="toggle(this)">x</span>'
        assert find_inline_code(html) == ['<span onclick="toggle(this)">']

    def test_style_attribute_is_found(self) -> None:
        html = '<form style="display:inline"></form>'
        assert find_inline_code(html) == ['<form style="display:inline">']

    def test_style_attribute_on_self_closing_svg_element_is_found(self) -> None:
        html = '<svg><path style="fill: red" /></svg>'
        assert find_inline_code(html) == ['<path style="fill: red" />']

    def test_javascript_url_is_found(self) -> None:
        html = '<a href="javascript:alert(1)">x</a>'
        assert find_inline_code(html) == ['<a href="javascript:alert(1)">']

    def test_javascript_text_in_other_attributes_is_allowed(self) -> None:
        assert not find_inline_code('<input value="javascript: a book">')
