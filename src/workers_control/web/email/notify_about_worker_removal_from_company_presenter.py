from dataclasses import dataclass
from html import escape

from workers_control.core.email_notifications import WorkerRemovalNotification
from workers_control.web.email import EmailConfiguration, MailService
from workers_control.web.translator import Translator
from workers_control.web.url_index import UrlIndex


@dataclass
class NotifyAboutWorkerRemovalPresenter:
    email_service: MailService
    email_configuration: EmailConfiguration
    translator: Translator
    url_index: UrlIndex

    def notify(self, message_data: WorkerRemovalNotification) -> None:
        self.email_service.send_message(
            subject=self.translator.gettext("Worker removed from company"),
            recipients=[message_data.worker_email, message_data.company_email],
            html=self.translator.gettext(
                "Hello,<br><br>The worker %(worker_name)s (id: %(worker_id)s) has been removed from company %(company_name)s."
                % dict(
                    worker_name=escape(message_data.worker_name),
                    worker_id=message_data.worker_id,
                    company_name=escape(message_data.company_name),
                )
            ),
            sender=self.email_configuration.get_sender_address(),
        )
