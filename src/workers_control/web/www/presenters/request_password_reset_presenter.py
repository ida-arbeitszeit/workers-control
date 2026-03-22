from dataclasses import dataclass

from workers_control.web.notification import Notifier
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex


@dataclass
class RequestPasswordResetPresenter:
    @dataclass
    class ViewModel:
        redirect_url: str

    notifier: Notifier
    translator: Translator
    url_index: UrlIndex

    def present_password_reset_request(self) -> ViewModel:
        self.notifier.display_info(
            self.translator.gettext(
                "If an account with that email exists, we have sent a password reset link."
            )
        )
        return self.ViewModel(
            redirect_url=self.url_index.get_request_password_reset_url()
        )
