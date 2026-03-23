from dataclasses import dataclass
from typing import Optional

from workers_control.core.interactors.show_basic_service import (
    ShowBasicServiceResponse,
)
from workers_control.web.formatters.datetime_formatter import DatetimeFormatter
from workers_control.web.translator import Translator


@dataclass
class ShowBasicServicePresenter:
    @dataclass
    class ViewModel:
        provider_name: str
        name: str
        description: str
        created_on: str

    translator: Translator
    datetime_formatter: DatetimeFormatter

    def present(self, response: ShowBasicServiceResponse) -> Optional[ViewModel]:
        if (details := response.details) is None:
            return None
        return self.ViewModel(
            provider_name=details.provider_name,
            name=details.name,
            description=details.description,
            created_on=self.datetime_formatter.format_datetime(
                date=details.created_on,
                fmt="%d.%m.%Y %H:%M",
            ),
        )
