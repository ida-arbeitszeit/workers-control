from dataclasses import dataclass

from workers_control.core import email_notifications
from workers_control.web.email import EmailConfiguration, MailService
from workers_control.web.text_renderer import TextRenderer
from workers_control.web.translator import Translator


@dataclass
class EmailChangeWarningView:
    email_service: MailService
    text_renderer: TextRenderer
    translator: Translator
    email_configuration: EmailConfiguration

    def render_email_change_warning(
        self, email_change_warning: email_notifications.EmailChangeWarning
    ) -> None:
        self.email_service.send_message(
            subject=self.translator.gettext("Email address change requested"),
            sender=self.email_configuration.get_sender_address(),
            html=self.text_renderer.render_email_change_warning(
                admin_email_address=self.email_configuration.get_admin_email_address(),
            ),
            recipients=[email_change_warning.old_email_address],
        )
