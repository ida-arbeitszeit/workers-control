from abc import ABC, abstractmethod


class EmailSenderPlugin(ABC):
    @abstractmethod
    def send_message(
        self,
        subject: str,
        recipient: list[str],
        html: str,
        sender: str,
    ) -> None:
        pass
