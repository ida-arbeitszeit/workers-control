from dataclasses import dataclass
from html import escape

from workers_control.core.email_notifications import CooperationRequestEmail
from workers_control.web.email import EmailConfiguration, MailService
from workers_control.web.translator import Translator


@dataclass
class CooperationRequestEmailPresenter:
    translator: Translator
    mail_service: MailService
    email_configuration: EmailConfiguration

    def present(self, email: CooperationRequestEmail) -> None:
        self.mail_service.send_message(
            subject=self.translator.gettext("A company requests cooperation"),
            recipients=[email.coordinator_email_address],
            html=self.translator.gettext(
                "Hello %(coordinator)s,<br>A company wants to be part of a cooperation that you are coordinating. Please check the request in the Workers Control app."
            )
            % dict(coordinator=escape(email.coordinator_name)),
            sender=self.email_configuration.get_sender_address(),
        )
