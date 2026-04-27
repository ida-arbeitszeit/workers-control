from urllib.parse import parse_qs, urlparse
from uuid import uuid4

from parameterized import parameterized

from tests.web.base_test_case import BaseTestCase
from tests.web.www.presenters.data_generators import QueriedOfferGenerator
from workers_control.web.pagination import PAGE_PARAMETER_NAME
from workers_control.web.session import UserRole
from workers_control.web.www.presenters.query_offers_presenter import (
    QueryOffersPresenter,
)


class QueryOffersPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(QueryOffersPresenter)
        self.queried_offer_generator = QueriedOfferGenerator()
        self.session.login_member(uuid4())

    def test_presenting_empty_response_leads_to_not_showing_results(self) -> None:
        response = self.queried_offer_generator.get_response([])
        presentation = self.presenter.present(response)
        self.assertFalse(presentation.show_results)

    def test_empty_view_model_does_not_show_results(self) -> None:
        presentation = self.presenter.get_empty_view_model()
        self.assertFalse(presentation.show_results)

    def test_non_empty_interactor_response_leads_to_showing_results(self) -> None:
        response = self.queried_offer_generator.get_response(
            [self.queried_offer_generator.get_plan()]
        )
        presentation = self.presenter.present(response)
        self.assertTrue(presentation.show_results)

    @parameterized.expand(
        [
            (-1,),
            (0,),
            (1,),
            (2,),
        ]
    )
    def test_correct_number_of_total_results_is_passed_on_to_view_model(
        self,
        number_of_results: int,
    ) -> None:
        response = self.queried_offer_generator.get_response(
            total_results=number_of_results
        )
        presentation = self.presenter.present(response)
        self.assertEqual(presentation.total_results, number_of_results)

    def test_correct_plan_url_is_shown(self) -> None:
        plan_id = uuid4()
        response = self.queried_offer_generator.get_response(
            [self.queried_offer_generator.get_plan(plan_id=plan_id)]
        )
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertEqual(
            table_row.offer_details_url,
            self.url_index.get_plan_details_url(
                user_role=UserRole.member, plan_id=plan_id
            ),
        )

    def test_correct_company_url_is_shown(self) -> None:
        company_id = uuid4()
        response = self.queried_offer_generator.get_response(
            [self.queried_offer_generator.get_plan(company_id=company_id)]
        )
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertEqual(
            table_row.provider_url,
            self.url_index.get_company_summary_url(company_id=company_id),
        )

    def test_correct_company_name_is_shown(self) -> None:
        response = self.queried_offer_generator.get_response(
            [self.queried_offer_generator.get_plan()]
        )
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertEqual(table_row.provider_name, "Planner name")

    def test_no_coop_is_shown_with_one_non_cooperating_plan(self) -> None:
        response = self.queried_offer_generator.get_response(
            [self.queried_offer_generator.get_plan(is_cooperating=False)]
        )
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertEqual(
            table_row.is_cooperating,
            False,
        )

    def test_coop_is_shown_with_one_cooperating_plan(self) -> None:
        response = self.queried_offer_generator.get_response(
            [self.queried_offer_generator.get_plan(is_cooperating=True)]
        )
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertEqual(
            table_row.is_cooperating,
            True,
        )

    def test_public_service_bool_is_passed_on_to_view_model(self) -> None:
        response = self.queried_offer_generator.get_response(
            [self.queried_offer_generator.get_plan()]
        )
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertEqual(
            table_row.is_public_service,
            False,
        )

    @parameterized.expand([(True,), (False,)])
    def test_that_is_expired_bool_is_passed_on_to_view_model(
        self, is_expired: bool
    ) -> None:
        response = self.queried_offer_generator.get_response(
            [self.queried_offer_generator.get_plan(is_expired=is_expired)]
        )
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertEqual(
            table_row.is_expired,
            is_expired,
        )

    def test_that_description_is_shown_without_line_returns(self) -> None:
        response = self.queried_offer_generator.get_response(
            [self.queried_offer_generator.get_plan()]
        )
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertIn("For eatingNext paragraphThird one", table_row.description)

    def test_that_only_first_few_chars_of_description_are_shown(self) -> None:
        description = "For eating\nNext paragraph\rThird one Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores."
        expected_substring = "For eatingNext paragraphThird one"
        unexpected_substring = "et accusam et justo duo dolores."
        response = self.queried_offer_generator.get_response(
            [self.queried_offer_generator.get_plan(description=description)]
        )
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertIn(expected_substring, table_row.description)
        self.assertNotIn(unexpected_substring, table_row.description)

    def test_that_with_only_1_plan_in_response_no_page_links_are_returned(self) -> None:
        response = self.queried_offer_generator.get_response(total_results=1)
        view_model = self.presenter.present(response)
        assert not view_model.pagination.is_visible

    def test_that_with_16_plans_in_response_the_pagination_is_visible(self) -> None:
        response = self.queried_offer_generator.get_response(total_results=16)
        view_model = self.presenter.present(response)
        assert view_model.pagination.is_visible

    def test_that_with_15_plans_in_response_the_pagination_is_not_visible(self) -> None:
        response = self.queried_offer_generator.get_response(total_results=15)
        view_model = self.presenter.present(response)
        assert not view_model.pagination.is_visible

    def test_that_with_16_plans_there_are_2_pages(self) -> None:
        response = self.queried_offer_generator.get_response(total_results=16)
        view_model = self.presenter.present(response)
        assert len(view_model.pagination.pages) == 2

    def test_that_with_31_plans_there_are_3_pages(self) -> None:
        response = self.queried_offer_generator.get_response(total_results=31)
        view_model = self.presenter.present(response)
        assert len(view_model.pagination.pages) == 3

    def test_that_with_30_plans_there_are_2_pages(self) -> None:
        response = self.queried_offer_generator.get_response(total_results=30)
        view_model = self.presenter.present(response)
        assert len(view_model.pagination.pages) == 2

    def test_that_label_of_first_page_is_1(self) -> None:
        response = self.queried_offer_generator.get_response(total_results=30)
        view_model = self.presenter.present(response)
        assert view_model.pagination.pages[0].label == "1"

    def test_that_label_of_second_page_is_2(self) -> None:
        response = self.queried_offer_generator.get_response(total_results=30)
        view_model = self.presenter.present(response)
        assert view_model.pagination.pages[1].label == "2"

    def test_with_requested_offset_of_0_the_first_page_is_current(self) -> None:
        response = self.queried_offer_generator.get_response(requested_offset=0)
        view_model = self.presenter.present(response)
        assert view_model.pagination.pages[0].is_current

    def test_with_requested_offset_of_0_the_second_page_is_not_current(self) -> None:
        response = self.queried_offer_generator.get_response(
            requested_offset=0, total_results=30
        )
        view_model = self.presenter.present(response)
        assert not view_model.pagination.pages[1].is_current

    @parameterized.expand(
        [
            (1,),
            (2,),
            (3,),
        ]
    )
    def test_that_correct_pages_are_shown_as_currently_selected(
        self,
        page_number_in_query_string: int,
    ) -> None:
        self.request.set_arg(PAGE_PARAMETER_NAME, str(page_number_in_query_string))
        response = self.queried_offer_generator.get_response(total_results=100)
        view_model = self.presenter.present(response)
        for index, page in enumerate(view_model.pagination.pages):
            if index == page_number_in_query_string - 1:
                assert page.is_current
            else:
                assert not page.is_current

    def test_that_page_links_generated_contain_page_number_in_query_args(self) -> None:
        response = self.queried_offer_generator.get_response(total_results=45)
        view_model = self.presenter.present(response)
        for n, page in enumerate(view_model.pagination.pages):
            self._assertQueryArg(page.href, name="page", value=str(n + 1))

    def test_that_other_query_arguments_are_preserved_when_generating_page_links(
        self,
    ) -> None:
        expected_name = "name123"
        expected_value = "value123"
        self.request.set_arg(expected_name, expected_value)
        response = self.queried_offer_generator.get_response(total_results=1)
        view_model = self.presenter.present(response)
        self._assertQueryArg(
            view_model.pagination.pages[0].href,
            name=expected_name,
            value=expected_value,
        )

    def test_that_page_links_lead_to_same_scheme_and_domain_as_original_page(
        self,
    ) -> None:
        expected_url = "url://some_url_with_pagination"
        self.request.set_request_target(expected_url)
        self.session.login_member(uuid4())
        response = self.queried_offer_generator.get_response(total_results=1)
        view_model = self.presenter.present(response)
        page_url = view_model.pagination.pages[0].href
        self._assertSameUrlScheme(page_url, expected_url)
        self._assertSameUrlDomain(page_url, expected_url)

    def _assertQueryArg(self, url: str, *, name: str, value: str) -> None:
        query_args = parse_qs(urlparse(url).query)
        assert name in query_args, f"Value for {name} was not found in query of {url}"
        assert (
            len(query_args[name]) == 1
        ), f"More the one value for {name} found in query args of {url}"
        assert (
            query_args[name][0] == value
        ), f"For query argument {name} expected {value} but found {query_args[name][0]}"

    def _assertSameUrlScheme(self, first: str, second: str) -> None:
        first_scheme = urlparse(first).scheme
        second_scheme = urlparse(second).scheme
        assert first_scheme == second_scheme

    def _assertSameUrlDomain(self, first: str, second: str) -> None:
        first_domain = urlparse(first).netloc
        second_domain = urlparse(second).netloc
        assert first_domain == second_domain


class MyPlanFlagTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(QueryOffersPresenter)
        self.queried_offer_generator = QueriedOfferGenerator()

    def test_is_own_plan_true_when_logged_in_company_matches_planner(self) -> None:
        company_id = uuid4()
        self.session.login_company(company_id)
        response = self.queried_offer_generator.get_response(
            [self.queried_offer_generator.get_plan(company_id=company_id)]
        )
        presentation = self.presenter.present(response)
        self.assertTrue(presentation.results.rows[0].is_own_plan)

    def test_is_own_plan_false_when_logged_in_company_is_not_the_planner(self) -> None:
        self.session.login_company(uuid4())
        response = self.queried_offer_generator.get_response(
            [self.queried_offer_generator.get_plan(company_id=uuid4())]
        )
        presentation = self.presenter.present(response)
        self.assertFalse(presentation.results.rows[0].is_own_plan)

    def test_is_own_plan_false_when_user_is_a_member(self) -> None:
        member_id = uuid4()
        self.session.login_member(member_id)
        response = self.queried_offer_generator.get_response(
            [self.queried_offer_generator.get_plan(company_id=member_id)]
        )
        presentation = self.presenter.present(response)
        self.assertFalse(presentation.results.rows[0].is_own_plan)

    def test_is_own_plan_false_when_user_is_an_accountant(self) -> None:
        accountant_id = uuid4()
        self.session.login_accountant(accountant_id)
        response = self.queried_offer_generator.get_response(
            [self.queried_offer_generator.get_plan(company_id=accountant_id)]
        )
        presentation = self.presenter.present(response)
        self.assertFalse(presentation.results.rows[0].is_own_plan)

    def test_is_own_basic_service_false_for_plan_offer(self) -> None:
        member_id = uuid4()
        self.session.login_member(member_id)
        response = self.queried_offer_generator.get_response(
            [self.queried_offer_generator.get_plan(company_id=member_id)]
        )
        presentation = self.presenter.present(response)
        self.assertFalse(presentation.results.rows[0].is_own_basic_service)


class MyBasicServiceFlagTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(QueryOffersPresenter)
        self.queried_offer_generator = QueriedOfferGenerator()

    def test_is_own_basic_service_true_when_logged_in_member_matches_provider(
        self,
    ) -> None:
        member_id = uuid4()
        self.session.login_member(member_id)
        response = self.queried_offer_generator.get_response(
            [self.queried_offer_generator.get_basic_service(provider_id=member_id)]
        )
        presentation = self.presenter.present(response)
        self.assertTrue(presentation.results.rows[0].is_own_basic_service)

    def test_is_own_basic_service_false_when_logged_in_member_is_not_the_provider(
        self,
    ) -> None:
        self.session.login_member(uuid4())
        response = self.queried_offer_generator.get_response(
            [self.queried_offer_generator.get_basic_service(provider_id=uuid4())]
        )
        presentation = self.presenter.present(response)
        self.assertFalse(presentation.results.rows[0].is_own_basic_service)

    def test_is_own_basic_service_false_when_user_is_a_company(self) -> None:
        company_id = uuid4()
        self.session.login_company(company_id)
        response = self.queried_offer_generator.get_response(
            [self.queried_offer_generator.get_basic_service(provider_id=company_id)]
        )
        presentation = self.presenter.present(response)
        self.assertFalse(presentation.results.rows[0].is_own_basic_service)

    def test_is_own_basic_service_false_when_user_is_an_accountant(self) -> None:
        accountant_id = uuid4()
        self.session.login_accountant(accountant_id)
        response = self.queried_offer_generator.get_response(
            [self.queried_offer_generator.get_basic_service(provider_id=accountant_id)]
        )
        presentation = self.presenter.present(response)
        self.assertFalse(presentation.results.rows[0].is_own_basic_service)

    def test_is_own_plan_false_for_basic_service_offer(self) -> None:
        member_id = uuid4()
        self.session.login_member(member_id)
        response = self.queried_offer_generator.get_response(
            [self.queried_offer_generator.get_basic_service(provider_id=member_id)]
        )
        presentation = self.presenter.present(response)
        self.assertFalse(presentation.results.rows[0].is_own_plan)


class ConsumptionIconTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(QueryOffersPresenter)
        self.queried_offer_generator = QueriedOfferGenerator()

    def test_icon_is_shown_to_members(self) -> None:
        self.session.login_member(uuid4())
        response = self.queried_offer_generator.get_response(
            [self.queried_offer_generator.get_plan()]
        )
        presentation = self.presenter.present(response)
        self.assertTrue(presentation.results.rows[0].show_consumption_icon)

    def test_icon_is_shown_to_companies(self) -> None:
        self.session.login_company(uuid4())
        response = self.queried_offer_generator.get_response(
            [self.queried_offer_generator.get_plan()]
        )
        presentation = self.presenter.present(response)
        self.assertTrue(presentation.results.rows[0].show_consumption_icon)

    def test_icon_is_hidden_from_accountants(self) -> None:
        self.session.login_accountant(uuid4())
        response = self.queried_offer_generator.get_response(
            [self.queried_offer_generator.get_plan()]
        )
        presentation = self.presenter.present(response)
        self.assertFalse(presentation.results.rows[0].show_consumption_icon)

    def test_member_consumption_url_is_private_consumption_url(self) -> None:
        self.session.login_member(uuid4())
        plan_id = uuid4()
        response = self.queried_offer_generator.get_response(
            [self.queried_offer_generator.get_plan(plan_id=plan_id)]
        )
        presentation = self.presenter.present(response)
        self.assertEqual(
            presentation.results.rows[0].consumption_url,
            self.url_index.get_register_private_consumption_url(plan_id=plan_id),
        )

    def test_company_consumption_url_is_productive_consumption_url(self) -> None:
        self.session.login_company(uuid4())
        plan_id = uuid4()
        response = self.queried_offer_generator.get_response(
            [self.queried_offer_generator.get_plan(plan_id=plan_id)]
        )
        presentation = self.presenter.present(response)
        self.assertEqual(
            presentation.results.rows[0].consumption_url,
            self.url_index.get_register_productive_consumption_url(plan_id=plan_id),
        )

    def test_accountant_has_empty_consumption_url(self) -> None:
        self.session.login_accountant(uuid4())
        response = self.queried_offer_generator.get_response(
            [self.queried_offer_generator.get_plan()]
        )
        presentation = self.presenter.present(response)
        self.assertEqual(presentation.results.rows[0].consumption_url, "")

    def test_consumption_is_disabled_for_members_on_expired_plans(self) -> None:
        self.session.login_member(uuid4())
        response = self.queried_offer_generator.get_response(
            [self.queried_offer_generator.get_plan(is_expired=True)]
        )
        presentation = self.presenter.present(response)
        self.assertTrue(presentation.results.rows[0].is_consumption_disabled)

    def test_consumption_is_enabled_for_members_on_active_plans(self) -> None:
        self.session.login_member(uuid4())
        response = self.queried_offer_generator.get_response(
            [self.queried_offer_generator.get_plan(is_expired=False)]
        )
        presentation = self.presenter.present(response)
        self.assertFalse(presentation.results.rows[0].is_consumption_disabled)

    def test_consumption_is_disabled_for_own_plan_even_when_active(self) -> None:
        company_id = uuid4()
        self.session.login_company(company_id)
        response = self.queried_offer_generator.get_response(
            [
                self.queried_offer_generator.get_plan(
                    company_id=company_id, is_expired=False
                )
            ]
        )
        presentation = self.presenter.present(response)
        self.assertTrue(presentation.results.rows[0].is_consumption_disabled)

    def test_consumption_is_enabled_for_company_on_foreign_active_plan(self) -> None:
        self.session.login_company(uuid4())
        response = self.queried_offer_generator.get_response(
            [
                self.queried_offer_generator.get_plan(
                    company_id=uuid4(), is_expired=False
                )
            ]
        )
        presentation = self.presenter.present(response)
        self.assertFalse(presentation.results.rows[0].is_consumption_disabled)


class BasicServiceRowTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(QueryOffersPresenter)
        self.generator = QueriedOfferGenerator()
        self.session.login_member(uuid4())

    def test_basic_service_row_is_marked_as_basic_service(self) -> None:
        response = self.generator.get_response([self.generator.get_basic_service()])
        presentation = self.presenter.present(response)
        self.assertTrue(presentation.results.rows[0].is_basic_service)

    def test_basic_service_row_has_empty_price(self) -> None:
        response = self.generator.get_response([self.generator.get_basic_service()])
        presentation = self.presenter.present(response)
        self.assertEqual(presentation.results.rows[0].price_per_unit, "")

    def test_basic_service_row_has_empty_provider_url(self) -> None:
        response = self.generator.get_response([self.generator.get_basic_service()])
        presentation = self.presenter.present(response)
        self.assertEqual(presentation.results.rows[0].provider_url, "")

    def test_basic_service_row_links_to_basic_service_details(self) -> None:
        bs_id = uuid4()
        response = self.generator.get_response(
            [self.generator.get_basic_service(basic_service_id=bs_id)]
        )
        presentation = self.presenter.present(response)
        self.assertEqual(
            presentation.results.rows[0].offer_details_url,
            self.url_index.get_basic_service_url(bs_id),
        )

    def test_basic_service_consumption_icon_is_shown_and_enabled_for_member(
        self,
    ) -> None:
        response = self.generator.get_response([self.generator.get_basic_service()])
        presentation = self.presenter.present(response)
        self.assertTrue(presentation.results.rows[0].show_consumption_icon)
        self.assertFalse(presentation.results.rows[0].is_consumption_disabled)

    def test_basic_service_consumption_url_links_to_register_view_for_member(
        self,
    ) -> None:
        bs_id = uuid4()
        response = self.generator.get_response(
            [self.generator.get_basic_service(basic_service_id=bs_id)]
        )
        presentation = self.presenter.present(response)
        self.assertEqual(
            presentation.results.rows[0].consumption_url,
            self.url_index.get_register_private_consumption_of_basic_service_url(
                basic_service_id=bs_id
            ),
        )

    def test_basic_service_consumption_icon_is_disabled_for_company(self) -> None:
        self.session.login_company(uuid4())
        response = self.generator.get_response([self.generator.get_basic_service()])
        presentation = self.presenter.present(response)
        self.assertTrue(presentation.results.rows[0].is_consumption_disabled)
        self.assertEqual(presentation.results.rows[0].consumption_url, "")

    def test_basic_service_consumption_icon_is_disabled_for_providing_member(
        self,
    ) -> None:
        provider_id = uuid4()
        self.session.login_member(provider_id)
        response = self.generator.get_response(
            [self.generator.get_basic_service(provider_id=provider_id)]
        )
        presentation = self.presenter.present(response)
        self.assertTrue(presentation.results.rows[0].is_consumption_disabled)
        self.assertEqual(presentation.results.rows[0].consumption_url, "")

    def test_basic_service_provider_name_is_passed_through(self) -> None:
        response = self.generator.get_response(
            [self.generator.get_basic_service(provider_name="Alice")]
        )
        presentation = self.presenter.present(response)
        self.assertEqual(presentation.results.rows[0].provider_name, "Alice")
