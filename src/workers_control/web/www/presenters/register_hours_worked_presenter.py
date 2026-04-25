from dataclasses import dataclass
from typing import Optional

from workers_control.core.interactors.register_hours_worked import (
    RegisterHoursWorkedResponse,
)
from workers_control.web.notification import Notifier
from workers_control.web.url_index import UrlIndex
from workers_control.web.www.controllers.register_hours_worked_controller import (
    ControllerRejection,
)
from workers_control.web.www.navbar import NavbarItem

from ...translator import Translator


@dataclass
class InteractorResponseViewModel:
    status_code: int
    redirect_url: Optional[str]


@dataclass
class RegisterHoursWorkedPresenter:
    notifier: Notifier
    translator: Translator
    url_index: UrlIndex

    def create_navbar_items(self) -> list[NavbarItem]:
        return [
            NavbarItem(
                text=self.translator.gettext("Registered working hours"),
                url=self.url_index.get_registered_hours_worked_url(),
            ),
            NavbarItem(
                text=self.translator.gettext("Register hours worked"),
                url=None,
            ),
        ]

    def present_interactor_response(
        self, response: RegisterHoursWorkedResponse
    ) -> InteractorResponseViewModel:
        if response.is_rejected:
            if (
                response.rejection_reason
                == RegisterHoursWorkedResponse.RejectionReason.worker_not_at_company
            ):
                self.notifier.display_warning(
                    self.translator.gettext(
                        "This worker does not work in your company."
                    )
                )
            return InteractorResponseViewModel(status_code=404, redirect_url=None)
        else:
            self.notifier.display_info(
                self.translator.gettext("Labour hours successfully registered")
            )
            return InteractorResponseViewModel(
                status_code=302,
                redirect_url=self.url_index.get_registered_hours_worked_url(),
            )

    def present_controller_warnings(
        self, controller_rejection: ControllerRejection
    ) -> None:
        if (
            controller_rejection.reason
            == ControllerRejection.RejectionReason.invalid_input
        ):
            self.notifier.display_warning(self.translator.gettext("Invalid input"))
        elif (
            controller_rejection.reason
            == ControllerRejection.RejectionReason.negative_amount
        ):
            self.notifier.display_warning(
                self.translator.gettext("A negative amount is not allowed.")
            )
