from dataclasses import dataclass
from decimal import Decimal

from workers_control.core.decimal import decimal_sum
from workers_control.core.records import SocialAccounting
from workers_control.core.repositories import DatabaseGateway


@dataclass
class PublicSectorFundService:
    database_gateway: DatabaseGateway
    social_accounting: SocialAccounting

    def calculate_psf_balance(self) -> Decimal:
        inbound = self.database_gateway.get_transfers().where_account_is_creditor(
            self.social_accounting.account_psf
        )
        outbound = self.database_gateway.get_transfers().where_account_is_debtor(
            self.social_accounting.account_psf
        )
        inbound_sum = decimal_sum(t.value for t in inbound)
        outbound_sum = decimal_sum(t.value for t in outbound)
        return inbound_sum - outbound_sum
