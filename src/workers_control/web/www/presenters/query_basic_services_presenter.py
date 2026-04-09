from dataclasses import dataclass

from workers_control.core.interactors.query_basic_services import (
    QueryBasicServicesResponse,
)
from workers_control.web.formatters.datetime_formatter import DatetimeFormatter
from workers_control.web.notification import Notifier
from workers_control.web.pagination import Pagination, Paginator
from workers_control.web.request import Request
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex


@dataclass
class ResultTableRow:
    basic_service_url: str
    provider_name: str
    name: str
    description: str
    created_on: str


@dataclass
class ResultsTable:
    rows: list[ResultTableRow]


@dataclass
class QueryBasicServicesViewModel:
    total_results: int
    results: ResultsTable
    show_results: bool
    pagination: Pagination


@dataclass
class QueryBasicServicesPresenter:
    url_index: UrlIndex
    user_notifier: Notifier
    translator: Translator
    request: Request
    datetime_formatter: DatetimeFormatter

    def present(
        self, response: QueryBasicServicesResponse
    ) -> QueryBasicServicesViewModel:
        if not response.results:
            self.user_notifier.display_warning(self.translator.gettext("No results."))
        return QueryBasicServicesViewModel(
            total_results=response.total_results,
            show_results=bool(response.results),
            results=ResultsTable(
                rows=[
                    ResultTableRow(
                        basic_service_url=self.url_index.get_basic_service_url(
                            result.id
                        ),
                        provider_name=result.provider_name,
                        name=result.name,
                        description="".join(result.description.splitlines())[:150],
                        created_on=self.datetime_formatter.format_datetime(
                            date=result.created_on,
                            fmt="%d.%m.%Y %H:%M",
                        ),
                    )
                    for result in response.results
                ],
            ),
            pagination=self._create_pagination(response),
        )

    def get_empty_view_model(self) -> QueryBasicServicesViewModel:
        return QueryBasicServicesViewModel(
            total_results=0,
            results=ResultsTable(rows=[]),
            show_results=False,
            pagination=Pagination(is_visible=False, pages=[]),
        )

    def _create_pagination(self, response: QueryBasicServicesResponse) -> Pagination:
        paginator = Paginator(
            request=self.request,
            total_results=response.total_results,
        )
        return Pagination(
            is_visible=paginator.number_of_pages > 1,
            pages=paginator.get_pages(),
        )
