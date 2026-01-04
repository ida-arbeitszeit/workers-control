from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from workers_control.core.records import SocialAccounting
from workers_control.core.services.account_details import (
    AccountDetailsService,
    AccountTransfer,
)


@dataclass
class ShowPSFAccountDetailsInteractor:
    @dataclass
    class Response:
        transfers: list[AccountTransfer]
        account_balance: Decimal

    account_details_service: AccountDetailsService
    social_accounting: SocialAccounting

    def show_details(self) -> Response:
        account = self.social_accounting.account_psf
        transfers = self.account_details_service.get_account_transfers(account)
        account_balance = self.account_details_service.get_account_balance(account)
        return self.Response(
            transfers=sorted(transfers, key=lambda t: t.date, reverse=True),
            account_balance=account_balance,
        )
