from dataclasses import dataclass

from workers_control.core.interactors.deactivate_basic_service import (
    Response,
)
from workers_control.web.translator import Translator

from ...notification import Notifier


@dataclass
class DeactivateBasicServicePresenter:
    notifier: Notifier
    trans: Translator

    def present(self, interactor_response: Response) -> None:
        if interactor_response.is_rejected:
            self.notifier.display_warning(
                self.trans.gettext("Could not deactivate basic service.")
            )
        else:
            self.notifier.display_info(
                self.trans.gettext("Basic service was deactivated.")
            )
