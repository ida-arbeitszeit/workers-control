from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from workers_control.core.interactors import (
    get_company_summary,
    show_member_account_details,
)


@dataclass
class AccountBalances:
    p_account: Decimal
    r_account: Decimal
    a_account: Decimal
    prd_account: Decimal


@dataclass
class BalanceChecker:
    get_company_summary_interactor: get_company_summary.GetCompanySummaryInteractor
    show_member_account_details_interactor: (
        show_member_account_details.ShowMemberAccountDetailsInteractor
    )

    def get_company_account_balances(self, company: UUID) -> AccountBalances:
        response = self.get_company_summary_interactor.execute(company_id=company)
        assert response
        return AccountBalances(
            p_account=response.account_balances.means,
            r_account=response.account_balances.raw_material,
            a_account=response.account_balances.work,
            prd_account=response.account_balances.product,
        )

    def get_member_account_balance(self, member: UUID) -> Decimal:
        response = self.show_member_account_details_interactor.execute(member_id=member)
        return response.balance
