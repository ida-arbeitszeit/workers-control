from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from tests.web.base_test_case import BaseTestCase
from tests.web.www.request import FakeRequest
from workers_control.core.interactors.query_offers import OfferFilter, OfferSorting
from workers_control.web.www.controllers.query_offers_controller import (
    QueryOffersController,
)


class QueryOffersControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(QueryOffersController)

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

    def test_that_offer_id_choice_produces_requests_filter_by_offer_id(self) -> None:
        request = self.controller.import_form_data(
            make_fake_form(filter_category="offer_id")
        )
        self.assertEqual(request.filter_category, OfferFilter.by_offer_id)

    def test_that_offer_name_choice_produces_requests_filter_by_offer_name(
        self,
    ) -> None:
        request = self.controller.import_form_data(
            make_fake_form(filter_category="offer_name")
        )
        self.assertEqual(request.filter_category, OfferFilter.by_offer_name)

    def test_that_random_filter_string_falls_back_to_filter_by_offer_name(
        self,
    ) -> None:
        request = self.controller.import_form_data(
            make_fake_form(filter_category="awqwrndaj")
        )
        self.assertEqual(request.filter_category, OfferFilter.by_offer_name)

    def test_that_default_request_model_includes_no_search_query(
        self,
    ) -> None:
        request = self.controller.import_form_data()
        self.assertIsNone(request.query_string)

    def test_that_empty_sorting_field_results_in_sorting_by_activation_date(
        self,
    ) -> None:
        request = self.controller.import_form_data()
        self.assertEqual(request.sorting_category, OfferSorting.by_activation)

    def test_that_nonexisting_sorting_field_results_in_sorting_by_activation_date(
        self,
    ) -> None:
        request = self.controller.import_form_data(
            form=make_fake_form(sorting_category="somethingjsbjbsd")
        )
        self.assertEqual(request.sorting_category, OfferSorting.by_activation)

    def test_that_provider_name_in_sorting_field_results_in_sorting_by_provider_name(
        self,
    ) -> None:
        request = self.controller.import_form_data(
            form=make_fake_form(sorting_category="provider_name")
        )
        self.assertEqual(request.sorting_category, OfferSorting.by_provider_name)

    def test_that_default_request_excludes_expired_plans(
        self,
    ) -> None:
        request = self.controller.import_form_data()
        self.assertFalse(request.include_expired_plans)

    def test_that_default_request_includes_basic_services(
        self,
    ) -> None:
        request = self.controller.import_form_data()
        self.assertTrue(request.include_basic_services)

    def test_that_form_value_for_include_basic_services_is_passed_through(
        self,
    ) -> None:
        request = self.controller.import_form_data(
            make_fake_form(include_basic_services=False)
        )
        self.assertFalse(request.include_basic_services)

    def test_that_form_value_for_include_expired_plans_is_passed_through(
        self,
    ) -> None:
        request = self.controller.import_form_data(
            make_fake_form(include_expired_plans=True)
        )
        self.assertTrue(request.include_expired_plans)


class PaginationTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(QueryOffersController)

    def test_if_no_page_is_specified_in_query_args_use_offset_of_0(
        self,
    ):
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

    def test_that_offset_0_is_assumed_if_no_valid_integer_is_specified_as_page(self):
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
    filter_category: Optional[str] = None,
    sorting_category: Optional[str] = None,
    include_expired_plans: Optional[bool] = None,
    include_basic_services: Optional[bool] = None,
) -> FakeQueryOffersForm:
    return FakeQueryOffersForm(
        query=query or "",
        offer_filter=filter_category or "offer_name",
        sorting_category=sorting_category or "activation",
        include_expired_plans=(
            include_expired_plans if include_expired_plans is not None else False
        ),
        include_basic_services=(
            include_basic_services if include_basic_services is not None else True
        ),
    )


@dataclass
class FakeQueryOffersForm:
    query: str
    offer_filter: str
    sorting_category: str
    include_expired_plans: bool
    include_basic_services: bool

    def get_query_string(self) -> str:
        return self.query

    def get_category_string(self) -> str:
        return self.offer_filter

    def get_radio_string(self) -> str:
        return self.sorting_category

    def get_include_expired_plans(self) -> bool:
        return self.include_expired_plans

    def get_include_basic_services(self) -> bool:
        return self.include_basic_services
