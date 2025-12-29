from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Iterable, Protocol

from workers_control.core.datetime_service import DatetimeService
from workers_control.core.repositories import DatabaseGateway


class PayoutFactorConfig(Protocol):
    def get_window_length_in_days(self) -> int: ...


@dataclass
class PlanInfo:
    is_public: bool
    l: Decimal
    p: Decimal
    r: Decimal
    start: datetime
    end: datetime
    coverage: Decimal


@dataclass
class PayoutFactorService:
    datetime_service: DatetimeService
    database_gateway: DatabaseGateway
    payout_factor_config: PayoutFactorConfig

    def calculate_current_payout_factor(self) -> Decimal:
        """
        The payout factor is calculated over a time window.
        See dev docs for an explanation.
        """
        now = self.datetime_service.now()
        relevant_plans = self._get_info_of_relevant_plans(now)
        return self._calculate_payout_factor(relevant_plans)

    def _get_info_of_relevant_plans(self, now: datetime) -> Iterable[PlanInfo]:
        window_length_in_days = self.payout_factor_config.get_window_length_in_days()
        window_start = now - timedelta(days=window_length_in_days / 2)
        window_end = now + timedelta(days=window_length_in_days / 2)
        plans = (
            self.database_gateway.get_plans()
            .that_were_approved_before(window_end)
            .that_will_expire_after(window_start)
        )

        for plan in plans:
            approval = plan.approval_date
            assert approval is not None
            expiration = plan.expiration_date
            assert expiration is not None

            coverage = self._calculate_coverage(
                window_start, window_end, approval, expiration
            )
            costs = plan.production_costs
            yield PlanInfo(
                is_public=plan.is_public_service,
                l=costs.labour_cost,
                p=costs.means_cost,
                r=costs.resource_cost,
                start=approval,
                end=expiration,
                coverage=coverage,
            )

    def _calculate_coverage(
        self,
        window_start: datetime,
        window_end: datetime,
        approval: datetime,
        expiration: datetime,
    ) -> Decimal:
        # coverage = fraction of plan's duration inside the window
        coverage_start = max(approval, window_start)
        coverage_end = min(expiration, window_end)

        plan_duration_days = (expiration - approval).days
        covered_days = max(0, (coverage_end - coverage_start).days)
        coverage = (
            Decimal(covered_days) / Decimal(plan_duration_days)
            if plan_duration_days > 0
            else Decimal(0)
        )
        return coverage

    @classmethod
    def _calculate_payout_factor(cls, plan_info: Iterable[PlanInfo]) -> Decimal:
        # payout factor or factor of individual consumption (FIC)
        # = (l − ( p_o + r_o )) / (l + l_o)
        # where:
        # l = labour in productive plans
        # l_o = labour in public plans
        # p_o = means of production in public plans
        # r_o = raw materials in public plans

        if not plan_info:
            return Decimal(1)

        l: Decimal = Decimal(0)
        l_o: Decimal = Decimal(0)
        p_o_and_r_o = Decimal(0)

        for plan in plan_info:
            if plan.is_public:
                l_o += plan.l * plan.coverage
                p_o_and_r_o += (plan.p + plan.r) * plan.coverage
            else:
                l += plan.l * plan.coverage
        total_labour = l + l_o

        if not total_labour:
            # prevent division by zero
            if p_o_and_r_o:
                return Decimal(0)
            return Decimal(1)

        possibly_negative_fic = (l - p_o_and_r_o) / total_labour
        return max(Decimal(0), possibly_negative_fic)
