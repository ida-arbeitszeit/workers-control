from dataclasses import dataclass

from workers_control.core.interactors.create_basic_service import (
    CreateBasicServiceResponse,
)

from ...notification import Notifier
from ...translator import Translator


@dataclass
class CreateBasicServiceViewModel:
    pass


@dataclass
class CreateBasicServicePresenter:
    user_notifier: Notifier
    translator: Translator

    def present(
        self, interactor_response: CreateBasicServiceResponse
    ) -> CreateBasicServiceViewModel:
        if not interactor_response.is_rejected:
            self.user_notifier.display_info(
                self.translator.gettext("Successfully created basic service.")
            )
        elif (
            interactor_response.rejection_reason
            == CreateBasicServiceResponse.RejectionReason.member_not_found
        ):
            self.user_notifier.display_warning(
                self.translator.gettext(
                    "Basic service creation failed: Member not found."
                )
            )
        return CreateBasicServiceViewModel()
