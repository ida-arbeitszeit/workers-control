from datetime import datetime
from urllib.parse import parse_qs, urlparse
from uuid import UUID, uuid4

from parameterized import parameterized

from tests.web.base_test_case import BaseTestCase
from workers_control.core.interactors.query_basic_services import (
    QueriedBasicService,
    QueryBasicServicesRequest,
    QueryBasicServicesResponse,
)
from workers_control.web.pagination import PAGE_PARAMETER_NAME
from workers_control.web.www.presenters.query_basic_services_presenter import (
    QueryBasicServicesPresenter,
)


class QueriedBasicServiceGenerator:
    def get_service(
        self,
        service_id: UUID | None = None,
        name: str = "Test Service",
        description: str = "For testing\nSecond paragraph\rThird one",
        provider_name: str = "Provider name",
        created_on: datetime | None = None,
    ) -> QueriedBasicService:
        if service_id is None:
            service_id = uuid4()
        if created_on is None:
            created_on = datetime.min
        return QueriedBasicService(
            id=service_id,
            name=name,
            description=description,
            provider_name=provider_name,
            created_on=created_on,
        )

    def get_response(
        self,
        services: list[QueriedBasicService] | None = None,
        total_results: int | None = None,
        query_string: str | None = None,
        requested_offset: int = 0,
        requested_limit: int | None = None,
    ) -> QueryBasicServicesResponse:
        if services is None:
            services = [self.get_service() for _ in range(5)]
        if total_results is None:
            total_results = max(len(services), 100)
        return QueryBasicServicesResponse(
            results=list(services),
            total_results=total_results,
            request=QueryBasicServicesRequest(
                query_string=query_string,
                offset=requested_offset,
                limit=requested_limit,
            ),
        )


class QueryBasicServicesPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(QueryBasicServicesPresenter)
        self.generator = QueriedBasicServiceGenerator()

    def test_presenting_empty_response_leads_to_not_showing_results(self) -> None:
        response = self.generator.get_response([])
        presentation = self.presenter.present(response)
        self.assertFalse(presentation.show_results)

    def test_empty_view_model_does_not_show_results(self) -> None:
        presentation = self.presenter.get_empty_view_model()
        self.assertFalse(presentation.show_results)

    def test_non_empty_interactor_response_leads_to_showing_results(self) -> None:
        response = self.generator.get_response([self.generator.get_service()])
        presentation = self.presenter.present(response)
        self.assertTrue(presentation.show_results)

    def test_show_warning_when_no_results_are_found(self) -> None:
        response = self.generator.get_response([])
        self.presenter.present(response)
        self.assertTrue(self.notifier.warnings)

    def test_dont_show_warning_when_results_are_found(self) -> None:
        response = self.generator.get_response([self.generator.get_service()])
        self.presenter.present(response)
        self.assertFalse(self.notifier.warnings)

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
        response = self.generator.get_response(total_results=number_of_results)
        presentation = self.presenter.present(response)
        self.assertEqual(presentation.total_results, number_of_results)

    def test_correct_basic_service_url_is_shown(self) -> None:
        service_id = uuid4()
        response = self.generator.get_response(
            [self.generator.get_service(service_id=service_id)]
        )
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertEqual(
            table_row.basic_service_url,
            self.url_index.get_basic_service_url(service_id),
        )

    def test_correct_provider_name_is_shown(self) -> None:
        response = self.generator.get_response(
            [self.generator.get_service(provider_name="Alice")]
        )
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertEqual(table_row.provider_name, "Alice")

    def test_correct_service_name_is_shown(self) -> None:
        response = self.generator.get_response(
            [self.generator.get_service(name="Haircut")]
        )
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertEqual(table_row.name, "Haircut")

    def test_that_description_is_shown_without_line_returns(self) -> None:
        response = self.generator.get_response([self.generator.get_service()])
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertIn("For testingSecond paragraphThird one", table_row.description)

    def test_that_only_first_few_chars_of_description_are_shown(self) -> None:
        description = "For testing\nSecond paragraph\rThird one Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores."
        expected_substring = "For testingSecond paragraphThird one"
        unexpected_substring = "et accusam et justo duo dolores."
        response = self.generator.get_response(
            [self.generator.get_service(description=description)]
        )
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        self.assertIn(expected_substring, table_row.description)
        self.assertNotIn(unexpected_substring, table_row.description)

    def test_created_on_is_formatted_via_datetime_formatter(self) -> None:
        created_on = datetime(2026, 3, 22, 12, 0)
        response = self.generator.get_response(
            [self.generator.get_service(created_on=created_on)]
        )
        presentation = self.presenter.present(response)
        table_row = presentation.results.rows[0]
        expected_formatted = self.datetime_formatter.format_datetime(
            date=created_on,
            fmt="%d.%m.%Y %H:%M",
        )
        self.assertEqual(table_row.created_on, expected_formatted)

    def test_that_with_only_1_service_in_response_no_page_links_are_returned(
        self,
    ) -> None:
        response = self.generator.get_response(total_results=1)
        view_model = self.presenter.present(response)
        assert not view_model.pagination.is_visible

    def test_that_with_16_services_in_response_the_pagination_is_visible(
        self,
    ) -> None:
        response = self.generator.get_response(total_results=16)
        view_model = self.presenter.present(response)
        assert view_model.pagination.is_visible

    def test_that_with_15_services_in_response_the_pagination_is_not_visible(
        self,
    ) -> None:
        response = self.generator.get_response(total_results=15)
        view_model = self.presenter.present(response)
        assert not view_model.pagination.is_visible

    def test_that_with_16_services_there_are_2_pages(self) -> None:
        response = self.generator.get_response(total_results=16)
        view_model = self.presenter.present(response)
        assert len(view_model.pagination.pages) == 2

    def test_that_with_31_services_there_are_3_pages(self) -> None:
        response = self.generator.get_response(total_results=31)
        view_model = self.presenter.present(response)
        assert len(view_model.pagination.pages) == 3

    def test_that_label_of_first_page_is_1(self) -> None:
        response = self.generator.get_response(total_results=30)
        view_model = self.presenter.present(response)
        assert view_model.pagination.pages[0].label == "1"

    def test_that_label_of_second_page_is_2(self) -> None:
        response = self.generator.get_response(total_results=30)
        view_model = self.presenter.present(response)
        assert view_model.pagination.pages[1].label == "2"

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
        response = self.generator.get_response(total_results=100)
        view_model = self.presenter.present(response)
        for index, page in enumerate(view_model.pagination.pages):
            if index == page_number_in_query_string - 1:
                assert page.is_current
            else:
                assert not page.is_current

    def test_that_page_links_generated_contain_page_number_in_query_args(self) -> None:
        response = self.generator.get_response(total_results=45)
        view_model = self.presenter.present(response)
        for n, page in enumerate(view_model.pagination.pages):
            self._assertQueryArg(page.href, name="page", value=str(n + 1))

    def test_that_other_query_arguments_are_preserved_when_generating_page_links(
        self,
    ) -> None:
        expected_name = "name123"
        expected_value = "value123"
        self.request.set_arg(expected_name, expected_value)
        response = self.generator.get_response(total_results=1)
        view_model = self.presenter.present(response)
        self._assertQueryArg(
            view_model.pagination.pages[0].href,
            name=expected_name,
            value=expected_value,
        )

    def _assertQueryArg(self, url: str, *, name: str, value: str) -> None:
        query_args = parse_qs(urlparse(url).query)
        assert name in query_args, f"Value for {name} was not found in query of {url}"
        assert (
            len(query_args[name]) == 1
        ), f"More than one value for {name} found in query args of {url}"
        assert (
            query_args[name][0] == value
        ), f"For query argument {name} expected {value} but found {query_args[name][0]}"
