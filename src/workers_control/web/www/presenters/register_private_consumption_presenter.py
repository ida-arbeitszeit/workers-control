from dataclasses import dataclass

from workers_control.core.interactors.register_private_consumption import (
    RegisterPrivateConsumptionResponse,
    RejectionReason,
)
from workers_control.web.forms import RegisterPrivateConsumptionForm
from workers_control.web.notification import Notifier
from workers_control.web.request import Request
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex
from workers_control.web.www.response import Redirect


@dataclass
class RenderForm:
    status_code: int
    form: RegisterPrivateConsumptionForm


RegisterPrivateConsumptionViewModel = Redirect | RenderForm


@dataclass
class RegisterPrivateConsumptionPresenter:
    user_notifier: Notifier
    translator: Translator
    url_index: UrlIndex

    def present(
        self,
        interactor_response: RegisterPrivateConsumptionResponse,
        request: Request,
    ) -> RegisterPrivateConsumptionViewModel:
        if interactor_response.rejection_reason is None:
            self.user_notifier.display_info(
                self.translator.gettext("Consumption successfully registered.")
            )
            return Redirect(url=self.url_index.get_register_private_consumption_url())
        form = self._create_form(request)
        status_code = 400
        if interactor_response.rejection_reason == RejectionReason.plan_inactive:
            form.plan_id_errors.append(
                self.translator.gettext(
                    "The specified plan has been expired. Please contact the selling company to provide you with an up-to-date plan ID."
                )
            )
            status_code = 410
        elif (
            interactor_response.rejection_reason == RejectionReason.insufficient_balance
        ):
            form.general_errors.append(
                self.translator.gettext("You do not have enough work certificates.")
            )
            status_code = 406
        elif (
            interactor_response.rejection_reason
            == RejectionReason.consumer_does_not_exist
        ):
            form.general_errors.append(
                self.translator.gettext(
                    "Failed to register private consumption. Are you logged in as a member?"
                )
            )
            status_code = 404
        else:
            form.plan_id_errors.append(
                self.translator.gettext(
                    "There is no plan with the specified ID in the database."
                )
            )
            status_code = 404
        return RenderForm(status_code=status_code, form=form)

    def _create_form(self, request: Request) -> RegisterPrivateConsumptionForm:
        return RegisterPrivateConsumptionForm(
            plan_id_value=request.get_form("plan_id") or "",
            amount_value=request.get_form("amount") or "",
        )
