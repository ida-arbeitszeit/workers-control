from arbeitszeit.injector import singleton


@singleton
class PayoutFactorConfigTestImpl:
    def __init__(self) -> None:
        self._window_length: int = 180

    def get_window_length_in_days(self) -> int:
        return self._window_length

    def set_window_length(self, days: int) -> None:
        self._window_length = days
