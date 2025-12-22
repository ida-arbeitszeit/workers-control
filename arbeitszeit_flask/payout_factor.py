from flask import current_app


class PayoutFactorConfigImpl:
    def get_window_length_in_days(self) -> int:
        value = current_app.config["PAYOUT_FACTOR_CALCULATION_WINDOW"]
        integer = int(value)
        if integer <= 0:
            raise ValueError()
        return integer
