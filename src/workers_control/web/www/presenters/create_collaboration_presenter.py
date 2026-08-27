from dataclasses import dataclass

from workers_control.core.interactors.create_collaboration import (
    CreateCollaborationResponse,
)

from ...notification import Notifier
from ...translator import Translator
from ...url_index import UrlIndex
from ..navbar import NavbarItem


@dataclass
class CreateCollaborationViewModel:
    pass


@dataclass(frozen=True)
class CreateCollaborationPresenter:
    user_notifier: Notifier
    translator: Translator
    url_index: UrlIndex

    def create_navbar_items(self) -> list[NavbarItem]:
        return [
            NavbarItem(
                text=self.translator.gettext("My collaborations"),
                url=self.url_index.get_my_collaborations_url(),
            ),
            NavbarItem(text=self.translator.gettext("Create Collaboration"), url=None),
        ]

    def present(
        self, interactor_response: CreateCollaborationResponse
    ) -> CreateCollaborationViewModel:
        if not interactor_response.is_rejected:
            self.user_notifier.display_info(
                self.translator.gettext("Successfully created collaboration.")
            )
        elif (
            interactor_response.rejection_reason
            == CreateCollaborationResponse.RejectionReason.collaboration_with_name_exists
        ):
            self.user_notifier.display_warning(
                self.translator.gettext(
                    "There is already a collaboration with the same name."
                )
            )
        elif (
            interactor_response.rejection_reason
            == CreateCollaborationResponse.RejectionReason.coordinator_not_found
        ):
            self.user_notifier.display_warning(
                self.translator.gettext("Internal error: Coordinator not found.")
            )
        return CreateCollaborationViewModel()
