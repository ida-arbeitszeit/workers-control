from dataclasses import dataclass

from workers_control.core.interactors.create_basic_service import (
    CreateBasicServiceResponse,
)

from ...notification import Notifier
from ...translator import Translator
from ...url_index import UrlIndex
from ..navbar import NavbarItem


@dataclass
class CreateBasicServiceViewModel:
    pass


@dataclass
class CreateBasicServicePresenter:
    user_notifier: Notifier
    translator: Translator
    url_index: UrlIndex

    def create_navbar_items(self) -> list[NavbarItem]:
        return [
            NavbarItem(
                text=self.translator.gettext("My basic services"),
                url=self.url_index.get_my_basic_services_url(),
            ),
            NavbarItem(text=self.translator.gettext("Create basic service"), url=None),
        ]

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
