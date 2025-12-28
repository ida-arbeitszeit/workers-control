from dataclasses import dataclass

from workers_control.core.interactors import change_user_email_address
from workers_control.web.notification import Notifier
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex


@dataclass
class ViewModel:
    redirect_url: str | None


@dataclass
class ChangeUserEmailAddressPresenter:
    notifier: Notifier
    url_index: UrlIndex
    translator: Translator

    def render_response(
        self, response: change_user_email_address.Response
    ) -> ViewModel:
        if response.is_rejected:
            self.notifier.display_warning(
                self.translator.gettext(
                    "Something went wrong. Perhaps the email address is not valid or already in use."
                )
            )
            return ViewModel(redirect_url=None)
        else:
            self.notifier.display_info(
                self.translator.gettext("Email address changed successfully.")
            )
            return ViewModel(redirect_url=self.url_index.get_user_account_details_url())
