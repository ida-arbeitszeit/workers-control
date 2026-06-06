from dataclasses import dataclass
from enum import Enum, auto

from workers_control.web.notification import Notifier
from workers_control.web.request import Request
from workers_control.web.translator import Translator


class ReviewDecision(Enum):
    approve = auto()
    reject = auto()


@dataclass
class ReviewPlanController:
    notifier: Notifier
    translator: Translator

    def process_review_form(self, request: Request) -> ReviewDecision | None:
        match request.get_form("decision"):
            case "approve":
                return ReviewDecision.approve
            case "reject":
                return ReviewDecision.reject
            case _:
                self.notifier.display_warning(
                    self.translator.gettext(
                        "Please choose whether to approve or reject the plan."
                    )
                )
                return None
