from abc import ABC, abstractmethod


class EmailPlugin(ABC):
    @abstractmethod
    def send_message(
        self,
        subject: str,
        recipients: list[str],
        html: str,
        sender: str,
    ) -> None:
        pass
