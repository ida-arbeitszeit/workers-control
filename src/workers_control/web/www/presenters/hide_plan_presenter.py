from dataclasses import dataclass

from workers_control.core.interactors.hide_plan import HidePlanResponse
from workers_control.web.translator import Translator

from ...notification import Notifier


@dataclass
class HidePlanPresenter:
    notifier: Notifier
    trans: Translator

    def present(self, interactor_response: HidePlanResponse) -> None:
        if interactor_response.is_success:
            self.notifier.display_info(
                self.trans.gettext(
                    "Expired plan %(plan_id)s is no longer shown to you."
                )
                % dict(plan_id=interactor_response.plan_id)
            )
