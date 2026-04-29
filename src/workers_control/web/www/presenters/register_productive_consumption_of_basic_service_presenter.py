from dataclasses import dataclass

from workers_control.core.interactors import (
    register_productive_consumption_of_basic_service,
)
from workers_control.web.forms import RegisterProductiveConsumptionOfBasicServiceForm
from workers_control.web.notification import Notifier
from workers_control.web.request import Request
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex
from workers_control.web.www.navbar import NavbarItem
from workers_control.web.www.response import Redirect


@dataclass
class RenderForm:
    status_code: int
    form: RegisterProductiveConsumptionOfBasicServiceForm


RegisterProductiveConsumptionOfBasicServiceViewModel = Redirect | RenderForm


@dataclass
class RegisterProductiveConsumptionOfBasicServicePresenter:
    user_notifier: Notifier
    translator: Translator
    url_index: UrlIndex

    def present(
        self,
        interactor_response: register_productive_consumption_of_basic_service.Response,
        request: Request,
    ) -> RegisterProductiveConsumptionOfBasicServiceViewModel:
        if interactor_response.rejection_reason is None:
            self.user_notifier.display_info(
                self.translator.gettext("Successfully registered.")
            )
            return Redirect(url=self.url_index.get_company_consumptions_url())
        form = self._create_form(request)
        status_code = 400
        if (
            interactor_response.rejection_reason
            == register_productive_consumption_of_basic_service.RejectionReason.basic_service_not_found
        ):
            form.basic_service_id_errors.append(
                self.translator.gettext(
                    "There is no basic service with the specified ID in the database."
                )
            )
            status_code = 404
        return RenderForm(status_code=status_code, form=form)

    def create_navbar_items(self) -> list[NavbarItem]:
        return [
            NavbarItem(
                text=self.translator.gettext("Offers"),
                url=self.url_index.get_query_offers_url(),
            ),
            NavbarItem(
                text=self.translator.gettext("Registration of productive consumption"),
                url=None,
            ),
        ]

    def _create_form(
        self, request: Request
    ) -> RegisterProductiveConsumptionOfBasicServiceForm:
        return RegisterProductiveConsumptionOfBasicServiceForm(
            basic_service_id_value=request.get_form("basic_service_id") or "",
            amount_value=request.get_form("amount") or "",
        )
