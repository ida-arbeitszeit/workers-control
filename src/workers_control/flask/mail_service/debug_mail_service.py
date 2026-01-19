from .interface import EmailPlugin


class DebugMailService(EmailPlugin):
    def send_message(
        self,
        subject: str,
        recipients: list[str],
        html: str,
        sender: str,
    ) -> None:
        print("Email would be sent:")
        print(f"recipients: {' '.join(recipients)}")
        print(f"subject: {subject}")
        print(f"sender: {sender}")
        print(f"content: {html}")
