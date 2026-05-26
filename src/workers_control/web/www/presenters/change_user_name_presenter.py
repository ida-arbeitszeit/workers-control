from dataclasses import dataclass
from typing import Optional

from workers_control.core.interactors import change_user_name as interactor
from workers_control.web.forms import ChangeUserNameForm
from workers_control.web.notification import Notifier
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex


@dataclass
class ViewModel:
    redirect_url: Optional[str]


@dataclass
class ChangeUserNamePresenter:
    url_index: UrlIndex
    notifier: Notifier
    translator: Translator

    def render_response(
        self, uc_response: interactor.Response, form: ChangeUserNameForm
    ) -> ViewModel:
        match uc_response.rejection_reason:
            case None:
                self._notify_about_acceptance()
                return ViewModel(
                    redirect_url=self.url_index.get_user_account_details_url()
                )
            case interactor.Response.RejectionReason.invalid_name:
                form.new_name_field.attach_error(
                    self.translator.gettext("The new name is invalid.")
                )
                self._notify_about_rejection()
                return ViewModel(redirect_url=None)
            case interactor.Response.RejectionReason.incorrect_password:
                form.current_password_field.attach_error(
                    self.translator.gettext("The password is incorrect.")
                )
                self._notify_about_rejection()
                return ViewModel(redirect_url=None)
            case interactor.Response.RejectionReason.user_not_found:
                self._notify_about_rejection()
                return ViewModel(redirect_url=None)

    def _notify_about_acceptance(self) -> None:
        self.notifier.display_info(
            self.translator.gettext("Your name has been changed.")
        )

    def _notify_about_rejection(self) -> None:
        self.notifier.display_warning(
            self.translator.gettext("Your request to change your name was rejected.")
        )
