from dataclasses import dataclass

from workers_control.core.interactors.delete_draft import DeleteDraftInteractor
from workers_control.web.notification import Notifier
from workers_control.web.session import Session
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex


@dataclass
class DeleteDraftPresenter:
    url_index: UrlIndex
    notifier: Notifier
    translator: Translator
    session: Session

    @dataclass
    class ViewModel:
        redirect_target: str

    def present_draft_deletion(
        self, response: DeleteDraftInteractor.Response
    ) -> ViewModel:
        self.notifier.display_info(
            self.translator.gettext(
                "Plan draft %(product_name)s was deleted"
                % dict(product_name=response.product_name)
            )
        )
        return self.ViewModel(
            redirect_target=self.session.pop_next_url()
            or self.url_index.get_my_plans_url()
        )
