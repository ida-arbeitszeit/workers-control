from dataclasses import dataclass
from decimal import Decimal

from workers_control.core.datetime_service import DatetimeService
from workers_control.core.repositories import DatabaseGateway
from workers_control.core.services.payout_factor import PayoutFactorService
from workers_control.core.services.psf_balance import PublicSectorFundService


@dataclass
class StatisticsResponse:
    registered_companies_count: int
    registered_members_count: int
    cooperations_count: int
    active_plans_count: int
    active_plans_public_count: int
    avg_timeframe: Decimal
    planned_work: Decimal
    planned_resources: Decimal
    planned_means: Decimal
    payout_factor: Decimal
    psf_balance: Decimal


@dataclass
class GetStatisticsInteractor:
    database: DatabaseGateway
    datetime_service: DatetimeService
    fic_service: PayoutFactorService
    psf_service: PublicSectorFundService

    def get_statistics(self) -> StatisticsResponse:
        fic = self.fic_service.calculate_current_payout_factor()
        psf_balance = self.psf_service.calculate_psf_balance()
        now = self.datetime_service.now()
        active_plans = (
            self.database.get_plans()
            .that_will_expire_after(now)
            .that_were_approved_before(now)
        )
        planning_statistics = active_plans.get_statistics()
        return StatisticsResponse(
            registered_companies_count=len(self.database.get_companies()),
            registered_members_count=len(self.database.get_members()),
            cooperations_count=len(self.database.get_cooperations()),
            active_plans_count=len(active_plans),
            active_plans_public_count=len(active_plans.that_are_public()),
            avg_timeframe=planning_statistics.average_plan_duration_in_days,
            planned_work=planning_statistics.total_planned_costs.labour_cost,
            planned_resources=planning_statistics.total_planned_costs.resource_cost,
            planned_means=planning_statistics.total_planned_costs.means_cost,
            payout_factor=fic,
            psf_balance=psf_balance,
        )
