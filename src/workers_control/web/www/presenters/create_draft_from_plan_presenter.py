from dataclasses import dataclass

from workers_control.core.interactors import create_draft_from_plan as interactor
from workers_control.web.notification import Notifier
from workers_control.web.request import Request
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex


@dataclass
class ViewModel:
    redirect_url: str


@dataclass
class CreateDraftFromPlanPresenter:
    url_index: UrlIndex
    notifier: Notifier
    translator: Translator

    def render_response(
        self,
        interactor_response: interactor.Response,
        request: Request,
    ) -> ViewModel:
        self.notifier.display_info(
            self.translator.gettext("A new draft was created from an expired plan.")
        )
        if interactor_response.draft:
            return ViewModel(
                redirect_url=self.url_index.get_draft_details_url(
                    interactor_response.draft
                )
            )
        else:
            return ViewModel(
                redirect_url=request.get_header("Referer")
                or self.url_index.get_my_plans_url()
            )
