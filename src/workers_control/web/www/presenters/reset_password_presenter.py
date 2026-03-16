from dataclasses import dataclass
from typing import Optional

from workers_control.core.interactors import change_user_password
from workers_control.web.notification import Notifier
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex


@dataclass
class ResetPasswordPresenter:
    @dataclass
    class ViewModel:
        redirect_url: Optional[str]

    notifier: Notifier
    translator: Translator
    url_index: UrlIndex

    def present_password_change(
        self, response: change_user_password.Response
    ) -> ViewModel:
        if response.is_changed:
            self.notifier.display_info(
                self.translator.gettext(
                    "Your password has been reset. You can now log in with your new password."
                )
            )
            return self.ViewModel(redirect_url=self.url_index.get_start_page_url())
        self.notifier.display_warning(
            self.translator.gettext("Password reset failed. Please try again.")
        )
        return self.ViewModel(
            redirect_url=self.url_index.get_request_password_reset_url()
        )
