from dataclasses import dataclass

from workers_control.core.interactors import edit_draft
from workers_control.web.notification import Notifier
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex


@dataclass
class ViewModel:
    redirect_url: str | None


@dataclass
class EditDraftPresenter:
    url_index: UrlIndex
    translator: Translator
    notifier: Notifier

    def render_response(self, response: edit_draft.Response) -> ViewModel:
        match response.rejection_reason:
            case edit_draft.Response.RejectionReason.NOT_FOUND:
                self.notifier.display_warning(
                    self.translator.gettext(
                        "The draft you are trying to edit does not exist."
                    )
                )
                return ViewModel(redirect_url=None)
            case edit_draft.Response.RejectionReason.UNAUTHORIZED:
                self.notifier.display_warning(
                    self.translator.gettext(
                        "You are not authorized to edit this draft."
                    )
                )
                return ViewModel(redirect_url=None)
            case None:
                return ViewModel(redirect_url=self.url_index.get_my_plans_url())
