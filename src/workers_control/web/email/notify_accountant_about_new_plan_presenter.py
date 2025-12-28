from dataclasses import dataclass

from workers_control.core.email_notifications import AccountantNotificationAboutNewPlan
from workers_control.web.email import EmailConfiguration, MailService
from workers_control.web.text_renderer import TextRenderer
from workers_control.web.translator import Translator


@dataclass
class NotifyAccountantsAboutNewPlanPresenterImpl:
    email_sender: MailService
    translator: Translator
    email_configuration: EmailConfiguration
    text_renderer: TextRenderer

    def notify_accountant_about_new_plan(
        self, notification: AccountantNotificationAboutNewPlan
    ) -> None:
        self.email_sender.send_message(
            self.translator.gettext("Plan was filed"),
            [notification.accountant_email_address],
            self.text_renderer.render_accountant_notification_about_new_plan(
                product_name=notification.product_name,
                accountant_name=notification.accountant_name,
            ),
            self.email_configuration.get_sender_address(),
        )
