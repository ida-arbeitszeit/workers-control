from dataclasses import dataclass

from workers_control.core import email_notifications
from workers_control.web.email import EmailConfiguration, MailService
from workers_control.web.text_renderer import TextRenderer
from workers_control.web.translator import Translator


@dataclass
class NameChangeConfirmationPresenter:
    email_service: MailService
    text_renderer: TextRenderer
    translator: Translator
    email_configuration: EmailConfiguration

    def present_name_change_confirmation(
        self, message: email_notifications.NameChangeConfirmation
    ) -> None:
        self.email_service.send_message(
            subject=self.translator.gettext("Your account name was changed"),
            sender=self.email_configuration.get_sender_address(),
            html=self.text_renderer.render_name_change_confirmation(
                new_name=message.new_name,
            ),
            recipients=[message.email_address],
        )
