from dataclasses import dataclass

from workers_control.core.interactors.register_private_consumption_of_basic_service import (
    RegisterPrivateConsumptionOfBasicServiceResponse,
    RejectionReason,
)
from workers_control.web.forms import RegisterPrivateConsumptionOfBasicServiceForm
from workers_control.web.notification import Notifier
from workers_control.web.request import Request
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex
from workers_control.web.www.navbar import NavbarItem
from workers_control.web.www.response import Redirect


@dataclass
class RenderForm:
    status_code: int
    form: RegisterPrivateConsumptionOfBasicServiceForm


RegisterPrivateConsumptionOfBasicServiceViewModel = Redirect | RenderForm


@dataclass
class RegisterPrivateConsumptionOfBasicServicePresenter:
    user_notifier: Notifier
    translator: Translator
    url_index: UrlIndex

    def present(
        self,
        interactor_response: RegisterPrivateConsumptionOfBasicServiceResponse,
        request: Request,
    ) -> RegisterPrivateConsumptionOfBasicServiceViewModel:
        if interactor_response.rejection_reason is None:
            self.user_notifier.display_info(
                self.translator.gettext("Consumption successfully registered.")
            )
            return Redirect(url=self.url_index.get_query_offers_url())
        form = self._create_form(request)
        status_code = 400
        if (
            interactor_response.rejection_reason
            == RejectionReason.basic_service_not_found
        ):
            form.basic_service_id_errors.append(
                self.translator.gettext(
                    "There is no basic service with the specified ID in the database."
                )
            )
            status_code = 404
        elif (
            interactor_response.rejection_reason
            == RejectionReason.consumer_does_not_exist
        ):
            form.general_errors.append(
                self.translator.gettext(
                    "Failed to register consumption. Are you logged in as a member?"
                )
            )
            status_code = 404
        elif (
            interactor_response.rejection_reason == RejectionReason.insufficient_balance
        ):
            form.general_errors.append(
                self.translator.gettext("You do not have enough work certificates.")
            )
            status_code = 406
        elif (
            interactor_response.rejection_reason == RejectionReason.consumer_is_provider
        ):
            form.general_errors.append(
                self.translator.gettext("You cannot consume your own basic service.")
            )
            status_code = 400
        return RenderForm(status_code=status_code, form=form)

    def create_navbar_items(self) -> list[NavbarItem]:
        return [
            NavbarItem(
                text=self.translator.gettext("Offers"),
                url=self.url_index.get_query_offers_url(),
            ),
            NavbarItem(
                text=self.translator.gettext("Register consumption"),
                url=None,
            ),
        ]

    def _create_form(
        self, request: Request
    ) -> RegisterPrivateConsumptionOfBasicServiceForm:
        return RegisterPrivateConsumptionOfBasicServiceForm(
            basic_service_id_value=request.get_form("basic_service_id") or "",
            amount_value=request.get_form("amount") or "",
        )
