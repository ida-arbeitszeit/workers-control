from dataclasses import dataclass

from workers_control.core.interactors.list_basic_services_of_worker import Response
from workers_control.web.formatters.datetime_formatter import DatetimeFormatter


@dataclass
class ListBasicServicesOfWorkerPresenter:
    @dataclass
    class ViewModel:
        @dataclass
        class Service:
            id: str
            name: str
            description: str
            created_on: str

        is_services_visible: bool
        services: list[Service]

    datetime_formatter: DatetimeFormatter

    def present(self, response: Response) -> ViewModel:
        return self.ViewModel(
            is_services_visible=bool(response.basic_services),
            services=[
                self.ViewModel.Service(
                    id=str(service.id),
                    name=service.name,
                    description=service.description,
                    created_on=self.datetime_formatter.format_datetime(
                        date=service.created_on,
                        fmt="%d.%m.%Y %H:%M",
                    ),
                )
                for service in response.basic_services
            ],
        )
