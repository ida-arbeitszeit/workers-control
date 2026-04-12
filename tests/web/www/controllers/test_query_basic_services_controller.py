from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from tests.web.base_test_case import BaseTestCase
from tests.web.www.request import FakeRequest
from workers_control.web.www.controllers.query_basic_services_controller import (
    QueryBasicServicesController,
)


class QueryBasicServicesControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(QueryBasicServicesController)

    def test_that_empty_query_string_translates_to_no_query_string_in_request(
        self,
    ) -> None:
        request = self.controller.import_form_data(make_fake_form(query=""))
        self.assertIsNone(request.query_string)

    def test_that_a_query_string_is_taken_as_the_literal_string_in_request(
        self,
    ) -> None:
        request = self.controller.import_form_data(make_fake_form(query="test"))
        self.assertEqual(request.query_string, "test")

    def test_that_leading_and_trailing_whitespaces_are_ignored(self) -> None:
        request = self.controller.import_form_data(make_fake_form(query=" test  "))
        self.assertEqual(request.query_string, "test")
        request = self.controller.import_form_data(make_fake_form(query="   "))
        self.assertIsNone(request.query_string)

    def test_that_default_request_model_includes_no_search_query(
        self,
    ) -> None:
        request = self.controller.import_form_data()
        self.assertIsNone(request.query_string)


class PaginationTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(QueryBasicServicesController)

    def test_if_no_page_is_specified_in_query_args_use_offset_of_0(
        self,
    ) -> None:
        request = FakeRequest()
        interactor_request = self.controller.import_form_data(request=request)
        assert interactor_request.offset == 0

    def test_that_without_request_specified_the_offset_is_set_to_0(self) -> None:
        interactor_request = self.controller.import_form_data(request=None)
        assert interactor_request.offset == 0

    def test_that_page_two_has_an_offset_of_15(self) -> None:
        request = FakeRequest()
        request.set_arg(arg="page", value="2")
        interactor_request = self.controller.import_form_data(request=request)
        assert interactor_request.offset == 15

    def test_that_offset_0_is_assumed_if_no_valid_integer_is_specified_as_page(
        self,
    ) -> None:
        request = FakeRequest()
        request.set_arg(arg="page", value="123abc")
        interactor_request = self.controller.import_form_data(request=request)
        assert interactor_request.offset == 0

    def test_that_offset_is_150_for_page_11(self) -> None:
        request = FakeRequest()
        request.set_arg(arg="page", value="11")
        interactor_request = self.controller.import_form_data(request=request)
        assert interactor_request.offset == 150

    def test_that_limit_is_15(self) -> None:
        request = FakeRequest()
        interactor_request = self.controller.import_form_data(request=request)
        assert interactor_request.limit == 15


def make_fake_form(
    query: Optional[str] = None,
) -> FakeQueryBasicServicesForm:
    return FakeQueryBasicServicesForm(
        query=query or "",
    )


@dataclass
class FakeQueryBasicServicesForm:
    query: str

    def get_query_string(self) -> str:
        return self.query
