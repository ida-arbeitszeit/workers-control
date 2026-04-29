from dataclasses import dataclass
from decimal import Decimal

from workers_control.core.interactors.select_productive_consumption_of_basic_service import (
    InvalidBasicServiceResponse,
    NoBasicServiceResponse,
    ValidBasicServiceResponse,
)
from workers_control.web.notification import Notifier
from workers_control.web.translator import Translator


@dataclass
class SelectProductiveConsumptionOfBasicServicePresenter:
    notifier: Notifier
    translator: Translator

    @dataclass
    class ViewModel:
        valid_basic_service_selected: bool
        basic_service_id: str | None
        basic_service_name: str | None
        basic_service_description: str | None
        provider_name: str | None
        amount: Decimal | None
        status_code: int

    def render_response(
        self,
        response: (
            NoBasicServiceResponse
            | InvalidBasicServiceResponse
            | ValidBasicServiceResponse
        ),
    ) -> ViewModel:
        if isinstance(response, NoBasicServiceResponse):
            return self.ViewModel(
                valid_basic_service_selected=False,
                basic_service_id=None,
                basic_service_name=None,
                basic_service_description=None,
                provider_name=None,
                amount=response.amount,
                status_code=200,
            )
        if isinstance(response, InvalidBasicServiceResponse):
            self.notifier.display_warning(
                self.translator.gettext("The selected basic service does not exist.")
            )
            return self.ViewModel(
                valid_basic_service_selected=False,
                basic_service_id=None,
                basic_service_name=None,
                basic_service_description=None,
                provider_name=None,
                amount=response.amount,
                status_code=404,
            )
        assert isinstance(response, ValidBasicServiceResponse)
        return self.ViewModel(
            valid_basic_service_selected=True,
            basic_service_id=str(response.basic_service_id),
            basic_service_name=response.basic_service_name,
            basic_service_description=response.basic_service_description,
            provider_name=response.provider_name,
            amount=response.amount,
            status_code=200,
        )
