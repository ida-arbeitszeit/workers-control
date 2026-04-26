from datetime import timedelta
from enum import Enum, auto
from uuid import UUID, uuid4

from parameterized import parameterized

from tests.datetime_service import datetime_utc
from tests.interactors.base_test_case import BaseTestCase
from workers_control.core.interactors.query_offers import (
    OfferFilter,
    OfferQueryResponse,
    OfferSorting,
    QueryOffersInteractor,
    QueryOffersRequest,
)


class SearchStrategy(Enum):
    by_id_sort_by_date_exclude_expired = auto()
    by_id_sort_by_date_include_expired = auto()
    by_id_sort_by_name_exclude_expired = auto()
    by_id_sort_by_name_include_expired = auto()
    by_name_sort_by_date_exclude_expired = auto()
    by_name_sort_by_date_include_expired = auto()
    by_name_sort_by_name_exclude_expired = auto()
    by_name_sort_by_name_include_expired = auto()


class InteractorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(QueryOffersInteractor)

    @parameterized.expand([(strategy,) for strategy in SearchStrategy])
    def test_that_no_plan_is_returned_when_searching_an_empty_repository(
        self,
        search_strategy: SearchStrategy,
    ) -> None:
        response = self.interactor.execute(self.make_request(search_strategy))
        assert not response.results

    @parameterized.expand([(strategy,) for strategy in SearchStrategy])
    def test_that_a_plan_awaiting_approval_is_not_returned(
        self,
        strategy: SearchStrategy,
    ) -> None:
        self.plan_generator.create_plan(approved=False)
        response = self.interactor.execute(self.make_request(strategy))
        assert not response.results

    @parameterized.expand([(strategy,) for strategy in SearchStrategy])
    def test_that_all_active_plans_are_returned(
        self,
        search_strategy: SearchStrategy,
    ) -> None:
        expected_number_of_plans = 3
        for _ in range(expected_number_of_plans):
            self.plan_generator.create_plan()
        response = self.interactor.execute(self.make_request(search_strategy))
        assert len(response.results) == expected_number_of_plans

    @parameterized.expand(
        [
            (SearchStrategy.by_id_sort_by_date_exclude_expired,),
            (SearchStrategy.by_name_sort_by_date_exclude_expired,),
            (SearchStrategy.by_id_sort_by_name_exclude_expired,),
            (SearchStrategy.by_name_sort_by_name_exclude_expired,),
        ]
    )
    def test_that_no_expired_plans_are_returned_when_they_are_excluded(
        self,
        search_strategy: SearchStrategy,
    ) -> None:
        expected_number_of_plans = 0
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        for _ in range(3):
            self.plan_generator.create_plan(timeframe=1)
        self.datetime_service.advance_time(timedelta(days=2))
        response = self.interactor.execute(self.make_request(search_strategy))
        assert len(response.results) == expected_number_of_plans

    def test_that_only_active_plan_is_returned_when_expired_plans_are_excluded(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        self.plan_generator.create_plan(timeframe=1)
        self.datetime_service.advance_time(timedelta(days=2))
        expected_plan = self.plan_generator.create_plan()
        response = self.interactor.execute(
            self.make_request(SearchStrategy.by_id_sort_by_date_exclude_expired)
        )
        assert len(response.results) == 1
        assert self.assertPlanInResults(expected_plan, response)

    @parameterized.expand(
        [
            (SearchStrategy.by_id_sort_by_date_include_expired,),
            (SearchStrategy.by_name_sort_by_date_include_expired,),
            (SearchStrategy.by_id_sort_by_name_include_expired,),
            (SearchStrategy.by_name_sort_by_name_include_expired,),
        ]
    )
    def test_that_expired_plans_are_returned_when_they_are_included(
        self,
        search_strategy: SearchStrategy,
    ) -> None:
        expected_number_of_plans = 3
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        for _ in range(expected_number_of_plans):
            self.plan_generator.create_plan(timeframe=1)
        self.datetime_service.advance_time(timedelta(days=2))
        response = self.interactor.execute(self.make_request(search_strategy))
        assert len(response.results) == expected_number_of_plans

    def test_that_expired_plan_is_shown_as_expired(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        self.plan_generator.create_plan(timeframe=1)
        self.datetime_service.advance_time(timedelta(days=2))
        response = self.interactor.execute(
            self.make_request(SearchStrategy.by_id_sort_by_date_include_expired)
        )
        assert response.results[0].is_expired

    def test_that_active_plan_is_not_shown_as_expired(
        self,
    ) -> None:
        self.plan_generator.create_plan()
        response = self.interactor.execute(self.make_request())
        assert not response.results[0].is_expired

    @parameterized.expand(
        [
            (SearchStrategy.by_id_sort_by_date_exclude_expired,),
            (SearchStrategy.by_id_sort_by_date_include_expired,),
            (SearchStrategy.by_id_sort_by_name_exclude_expired,),
            (SearchStrategy.by_id_sort_by_name_include_expired,),
        ]
    )
    def test_that_active_plan_where_id_is_exact_match_is_returned(
        self,
        search_strategy: SearchStrategy,
    ) -> None:
        self.plan_generator.create_plan()
        expected_plan = self.plan_generator.create_plan()
        response = self.interactor.execute(
            self.make_request(search_strategy=search_strategy, query=str(expected_plan))
        )
        assert len(response.results) == 1
        assert self.assertPlanInResults(expected_plan, response)

    def test_query_with_substring_of_id_returns_correct_plan(self) -> None:
        expected_plan = self.plan_generator.create_plan()
        substring_query = str(expected_plan)[5:10]
        response = self.interactor.execute(
            self.make_request(
                search_strategy=SearchStrategy.by_id_sort_by_date_exclude_expired,
                query=substring_query,
            )
        )
        assert self.assertPlanInResults(expected_plan, response)

    def test_that_plans_where_product_name_is_exact_match_are_returned(self) -> None:
        expected_plan = self.plan_generator.create_plan(product_name="Name XYZ")
        query = "Name XYZ"
        response = self.interactor.execute(
            self.make_request(
                search_strategy=SearchStrategy.by_name_sort_by_date_exclude_expired,
                query=query,
            )
        )
        assert self.assertPlanInResults(expected_plan, response)

    def test_query_with_substring_of_product_name_returns_correct_result(self) -> None:
        expected_plan = self.plan_generator.create_plan(product_name="Name XYZ")
        query = "me X"
        response = self.interactor.execute(
            self.make_request(
                search_strategy=SearchStrategy.by_name_sort_by_date_exclude_expired,
                query=query,
            )
        )
        assert self.assertPlanInResults(expected_plan, response)

    def test_query_with_substring_of_product_is_case_insensitive(self) -> None:
        expected_plan = self.plan_generator.create_plan(product_name="Name XYZ")
        query = "xyz"
        response = self.interactor.execute(
            self.make_request(
                search_strategy=SearchStrategy.by_name_sort_by_date_exclude_expired,
                query=query,
            )
        )
        assert self.assertPlanInResults(expected_plan, response)

    @parameterized.expand(
        [
            (SearchStrategy.by_id_sort_by_date_exclude_expired,),
            (SearchStrategy.by_id_sort_by_date_include_expired,),
            (SearchStrategy.by_name_sort_by_date_exclude_expired,),
            (SearchStrategy.by_name_sort_by_date_include_expired,),
        ]
    )
    def test_that_plans_are_returned_in_order_of_activation_with_newest_plan_first_when_requested(
        self,
        search_strategy: SearchStrategy,
    ) -> None:
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        expected_third = self.plan_generator.create_plan()
        self.datetime_service.advance_time(timedelta(days=1))
        expected_second = self.plan_generator.create_plan()
        self.datetime_service.advance_time(timedelta(days=1))
        expected_first = self.plan_generator.create_plan()
        self.datetime_service.advance_time(timedelta(days=1))
        response = self.interactor.execute(
            self.make_request(search_strategy=search_strategy)
        )
        assert response.results[0].id == expected_first
        assert response.results[1].id == expected_second
        assert response.results[2].id == expected_third

    @parameterized.expand(
        [
            (SearchStrategy.by_id_sort_by_name_exclude_expired,),
            (SearchStrategy.by_id_sort_by_name_include_expired,),
            (SearchStrategy.by_name_sort_by_name_exclude_expired,),
            (SearchStrategy.by_name_sort_by_name_include_expired,),
        ]
    )
    def test_that_plans_are_returned_sorted_by_company_name_when_requested(
        self,
        search_strategy: SearchStrategy,
    ) -> None:
        for name in ["c_name", "a_name", "B_name"]:
            self.plan_generator.create_plan(
                planner=self.company_generator.create_company(name=name),
            )
        response = self.interactor.execute(
            self.make_request(search_strategy=search_strategy)
        )
        assert response.results[0].provider_name == "a_name"
        assert response.results[1].provider_name == "B_name"
        assert response.results[2].provider_name == "c_name"

    @parameterized.expand(
        [
            (SearchStrategy.by_name_sort_by_date_exclude_expired,),
            (SearchStrategy.by_name_sort_by_date_include_expired,),
        ]
    )
    def test_that_plans_filtered_by_name_are_returned_sorted_by_date_if_requested(
        self,
        search_strategy: SearchStrategy,
    ) -> None:
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 4))
        expected_second = self.plan_generator.create_plan(product_name="abcde")
        self.datetime_service.advance_time(timedelta(days=1))
        expected_first = self.plan_generator.create_plan(product_name="xyabc")
        self.datetime_service.advance_time(timedelta(days=1))
        # unexpected plan
        self.plan_generator.create_plan(
            product_name="cba",
        )
        response = self.interactor.execute(
            self.make_request(
                search_strategy=search_strategy,
                query="abc",
            )
        )
        assert len(response.results) == 2
        assert response.results[0].id == expected_first
        assert response.results[1].id == expected_second

    def test_that_correct_price_per_unit_of_zero_is_displayed_for_a_public_plan(
        self,
    ) -> None:
        self.plan_generator.create_plan(is_public_service=True)
        response = self.interactor.execute(self.make_request())
        assert response.results[0].price_per_unit == 0

    def test_that_two_cooperating_plans_have_the_same_price(self) -> None:
        cooperation = self.cooperation_generator.create_cooperation()
        self.plan_generator.create_plan(cooperation=cooperation, amount=1000)
        self.plan_generator.create_plan(cooperation=cooperation, amount=1)
        response = self.interactor.execute(self.make_request())
        assert response.results[0].price_per_unit == response.results[1].price_per_unit

    def test_that_price_of_cooperating_plans_is_correct(
        self,
    ) -> None:
        cooperation = self.cooperation_generator.create_cooperation()
        plan1 = self.plan_generator.create_plan(
            cooperation=cooperation,
            amount=1000,
        )
        plan2 = self.plan_generator.create_plan(
            cooperation=cooperation,
            amount=1,
        )
        response = self.interactor.execute(self.make_request())
        assert response.results[
            0
        ].price_per_unit == self.price_checker.get_price_per_unit(plan1)
        assert response.results[
            1
        ].price_per_unit == self.price_checker.get_price_per_unit(plan2)

    @parameterized.expand(
        [
            (0,),
            (1,),
            (6,),
        ]
    )
    def test_total_results_equals_existing_plans_when_no_filter(
        self,
        number_of_plans: int,
    ) -> None:
        for _ in range(number_of_plans):
            self.plan_generator.create_plan()
        response = self.interactor.execute(self.make_request(query=""))
        assert response.total_results == number_of_plans

    def test_zero_total_results_when_single_plan_filtered_by_name(
        self,
    ) -> None:
        self.plan_generator.create_plan(product_name="abc")
        response = self.interactor.execute(
            self.make_request(
                search_strategy=SearchStrategy.by_name_sort_by_date_exclude_expired,
                query="xyz",
            )
        )
        self.assertEqual(response.total_results, 0)

    def test_zero_total_results_when_single_plan_filtered_by_id(
        self,
    ) -> None:
        self.plan_generator.create_plan()
        response = self.interactor.execute(
            self.make_request(
                search_strategy=SearchStrategy.by_id_sort_by_date_exclude_expired,
                query=f"{uuid4()}",
            )
        )
        self.assertEqual(response.total_results, 0)

    def test_that_first_10_plans_are_returned_if_limit_is_10(
        self,
    ) -> None:
        for _ in range(20):
            self.plan_generator.create_plan()
        response = self.interactor.execute(self.make_request(limit=10))
        assert len(response.results) == 10

    def test_that_all_plans_are_returned_if_limit_is_0_and_there_are_20_plans(
        self,
    ) -> None:
        for _ in range(20):
            self.plan_generator.create_plan()
        response = self.interactor.execute(self.make_request())
        assert len(response.results) == 20

    def test_that_5_plans_are_returned_on_second_page_if_20_plans_exist_and_offset_is_15(
        self,
    ) -> None:
        for _ in range(20):
            self.plan_generator.create_plan()
        response = self.interactor.execute(self.make_request(offset=15))
        assert len(response.results) == 5

    def make_request(
        self,
        search_strategy: SearchStrategy | None = None,
        query: str | None = None,
        offset: int | None = None,
        limit: int | None = None,
    ) -> QueryOffersRequest:
        if search_strategy is None:
            search_strategy = SearchStrategy.by_name_sort_by_date_exclude_expired
        match search_strategy:
            case SearchStrategy.by_id_sort_by_date_exclude_expired:
                category = OfferFilter.by_offer_id
                sorting = OfferSorting.by_activation
                include_expired_plans = False
            case SearchStrategy.by_id_sort_by_date_include_expired:
                category = OfferFilter.by_offer_id
                sorting = OfferSorting.by_activation
                include_expired_plans = True
            case SearchStrategy.by_id_sort_by_name_exclude_expired:
                category = OfferFilter.by_offer_id
                sorting = OfferSorting.by_provider_name
                include_expired_plans = False
            case SearchStrategy.by_id_sort_by_name_include_expired:
                category = OfferFilter.by_offer_id
                sorting = OfferSorting.by_provider_name
                include_expired_plans = True
            case SearchStrategy.by_name_sort_by_date_exclude_expired:
                category = OfferFilter.by_offer_name
                sorting = OfferSorting.by_activation
                include_expired_plans = False
            case SearchStrategy.by_name_sort_by_date_include_expired:
                category = OfferFilter.by_offer_name
                sorting = OfferSorting.by_activation
                include_expired_plans = True
            case SearchStrategy.by_name_sort_by_name_exclude_expired:
                category = OfferFilter.by_offer_name
                sorting = OfferSorting.by_provider_name
                include_expired_plans = False
            case SearchStrategy.by_name_sort_by_name_include_expired:
                category = OfferFilter.by_offer_name
                sorting = OfferSorting.by_provider_name
                include_expired_plans = True
        return QueryOffersRequest(
            query_string=query,
            filter_category=category,
            sorting_category=sorting,
            offset=offset,
            limit=limit,
            include_expired_plans=include_expired_plans,
            include_basic_services=False,
        )

    def assertPlanInResults(self, plan: UUID, response: OfferQueryResponse) -> bool:
        return any((plan == result.id for result in response.results))


class BasicServiceInteractorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(QueryOffersInteractor)

    def test_basic_services_are_returned_when_include_basic_services_is_true(
        self,
    ) -> None:
        bs = self.basic_service_generator.create_basic_service()
        response = self.interactor.execute(self._make_request())
        assert any(r.id == bs and r.is_basic_service for r in response.results)

    def test_basic_services_are_excluded_when_include_basic_services_is_false(
        self,
    ) -> None:
        self.basic_service_generator.create_basic_service()
        response = self.interactor.execute(
            self._make_request(include_basic_services=False)
        )
        assert not any(r.is_basic_service for r in response.results)

    def test_total_results_counts_plans_and_basic_services_combined(self) -> None:
        self.plan_generator.create_plan()
        self.basic_service_generator.create_basic_service()
        response = self.interactor.execute(self._make_request())
        assert response.total_results == 2

    def test_basic_service_can_be_filtered_by_name_substring(self) -> None:
        self.basic_service_generator.create_basic_service(name="Yoga lessons")
        self.basic_service_generator.create_basic_service(name="Plumbing")
        response = self.interactor.execute(self._make_request(query="yoga"))
        assert len(response.results) == 1
        assert response.results[0].is_basic_service
        assert response.results[0].name == "Yoga lessons"

    def test_basic_service_can_be_filtered_by_id_substring(self) -> None:
        bs = self.basic_service_generator.create_basic_service()
        substring = str(bs)[3:8]
        response = self.interactor.execute(
            self._make_request(
                query=substring,
                filter_category=OfferFilter.by_offer_id,
            )
        )
        assert any(r.id == bs for r in response.results)

    def test_basic_service_provider_name_is_returned(self) -> None:
        member = self.member_generator.create_member(name="Alice Provider")
        self.basic_service_generator.create_basic_service(member=member)
        response = self.interactor.execute(self._make_request())
        bs_results = [r for r in response.results if r.is_basic_service]
        assert bs_results
        assert bs_results[0].provider_name == "Alice Provider"

    def test_sort_by_provider_name_interleaves_plans_and_basic_services(self) -> None:
        member_a = self.member_generator.create_member(name="A_member")
        company_b = self.company_generator.create_company(name="B_company")
        self.basic_service_generator.create_basic_service(member=member_a)
        self.plan_generator.create_plan(planner=company_b)
        response = self.interactor.execute(
            self._make_request(sorting=OfferSorting.by_provider_name)
        )
        assert [r.provider_name for r in response.results] == [
            "A_member",
            "B_company",
        ]

    def _make_request(
        self,
        query: str | None = None,
        filter_category: OfferFilter = OfferFilter.by_offer_name,
        sorting: OfferSorting = OfferSorting.by_activation,
        include_basic_services: bool = True,
    ) -> QueryOffersRequest:
        return QueryOffersRequest(
            query_string=query,
            filter_category=filter_category,
            sorting_category=sorting,
            include_expired_plans=False,
            include_basic_services=include_basic_services,
        )
