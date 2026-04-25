from dataclasses import dataclass

from workers_control.core.interactors.file_plan_with_accounting import (
    FilePlanWithAccounting,
)
from workers_control.web.notification import Notifier
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex


@dataclass
class FilePlanWithAccountingPresenter:
    @dataclass
    class ViewModel:
        redirect_url: str

    url_index: UrlIndex
    notifier: Notifier
    translator: Translator

    def present_response(self, response: FilePlanWithAccounting.Response) -> ViewModel:
        redirect_url = self.url_index.get_my_plans_url()
        if response.plan_id is not None and response.is_plan_successfully_filed:
            self.notifier.display_info(
                self.translator.gettext(
                    "Successfully filed plan with social accounting"
                )
            )
        else:
            self.notifier.display_warning(
                self.translator.gettext("Could not file plan with social accounting")
            )
        return self.ViewModel(redirect_url=redirect_url)
