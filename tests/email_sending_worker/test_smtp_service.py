import socket
from smtplib import SMTPServerDisconnected
from unittest import TestCase

from workers_control.email_sending_worker.smtp_service import (
    SmtpMailServerConfig,
    SmtpMailService,
)


class SmtpMailServiceTimeoutTests(TestCase):
    def setUp(self) -> None:
        self.unresponsive_server = socket.socket()
        self.addCleanup(self.unresponsive_server.close)
        self.unresponsive_server.bind(("127.0.0.1", 0))
        self.unresponsive_server.listen()

    def _send_message(self, encryption_type: str) -> None:
        _, port = self.unresponsive_server.getsockname()
        service = SmtpMailService(
            config=SmtpMailServerConfig(
                mail_server="127.0.0.1",
                mail_port=port,
                encryption_type=encryption_type,
                timeout=0.3,
            )
        )
        service.send_message(
            subject="hello",
            recipient=["to@example.org"],
            html="<p>hi</p>",
            sender="from@example.org",
        )

    def test_sending_with_starttls_fails_when_server_does_not_respond(self) -> None:
        with self.assertRaises(SMTPServerDisconnected):
            self._send_message(encryption_type="tls")

    def test_sending_with_ssl_fails_when_server_does_not_respond(self) -> None:
        with self.assertRaises(TimeoutError):
            self._send_message(encryption_type="ssl")
