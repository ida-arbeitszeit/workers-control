from dataclasses import dataclass

from workers_control.core import email_notifications
from workers_control.web.email import EmailConfiguration, MailService
from workers_control.web.text_renderer import TextRenderer
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex


@dataclass
class ResetPasswordEmailPresenter:
    email_service: MailService
    url_index: UrlIndex
    email_configuration: EmailConfiguration
    translator: Translator
    text_renderer: TextRenderer

    def present_reset_password_request(
        self, message: email_notifications.ResetPasswordRequest
    ) -> None:
        self.email_service.send_message(
            subject=self.translator.gettext("Password reset requested"),
            recipients=[message.email_address],
            html=self.text_renderer.render_password_reset_request_email(
                reset_url=self.url_index.get_password_reset_url(
                    token=message.reset_token
                )
            ),
            sender=self.email_configuration.get_sender_address(),
        )

    def present_reset_password_confirmation(
        self, message: email_notifications.ResetPasswordConfirmation
    ) -> None:
        self.email_service.send_message(
            subject=self.translator.gettext("Password reset successful"),
            recipients=[message.email_address],
            html=self.text_renderer.render_password_reset_confirmation_email(),
            sender=self.email_configuration.get_sender_address(),
        )
