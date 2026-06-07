from dataclasses import dataclass

from workers_control.core.interactors.create_cooperation import (
    CreateCooperationResponse,
)

from ...notification import Notifier
from ...translator import Translator
from ...url_index import UrlIndex
from ..navbar import NavbarItem


@dataclass
class CreateCooperationViewModel:
    pass


@dataclass(frozen=True)
class CreateCooperationPresenter:
    user_notifier: Notifier
    translator: Translator
    url_index: UrlIndex

    def create_navbar_items(self) -> list[NavbarItem]:
        return [
            NavbarItem(
                text=self.translator.gettext("My cooperations"),
                url=self.url_index.get_my_cooperations_url(),
            ),
            NavbarItem(text=self.translator.gettext("Create Cooperation"), url=None),
        ]

    def present(
        self, interactor_response: CreateCooperationResponse
    ) -> CreateCooperationViewModel:
        if not interactor_response.is_rejected:
            self.user_notifier.display_info(
                self.translator.gettext("Successfully created cooperation.")
            )
        elif (
            interactor_response.rejection_reason
            == CreateCooperationResponse.RejectionReason.cooperation_with_name_exists
        ):
            self.user_notifier.display_warning(
                self.translator.gettext(
                    "There is already a cooperation with the same name."
                )
            )
        elif (
            interactor_response.rejection_reason
            == CreateCooperationResponse.RejectionReason.coordinator_not_found
        ):
            self.user_notifier.display_warning(
                self.translator.gettext("Internal error: Coordinator not found.")
            )
        return CreateCooperationViewModel()
