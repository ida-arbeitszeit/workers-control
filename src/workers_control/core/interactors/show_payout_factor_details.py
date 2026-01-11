from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID

from workers_control.core import records
from workers_control.core.datetime_service import DatetimeService
from workers_control.core.repositories import DatabaseGateway
from workers_control.core.services.payout_factor import (
    PayoutFactorConfig,
    PayoutFactorService,
)


@dataclass
class Response:
    payout_factor: Decimal
    window_center: datetime
    window_size_in_days: int
    window_start: datetime
    window_end: datetime
    plans: list[PlanData]


@dataclass
class PlanData:
    id_: UUID
    name: str
    approval_date: datetime
    expiration_date: datetime
    is_public_service: bool
    timeframe: int
    coverage: Decimal


@dataclass
class ShowPayoutFactorDetailsInteractor:
    payout_factor_config: PayoutFactorConfig
    datetime_service: DatetimeService
    database_gateway: DatabaseGateway
    payout_factor_service: PayoutFactorService

    def show_payout_factor_details(self) -> Response:
        now = self.datetime_service.now()
        window_size_in_days = self.payout_factor_config.get_window_length_in_days()
        window_start = now - timedelta(days=window_size_in_days / 2)
        window_end = now + timedelta(days=window_size_in_days / 2)
        plan_records = self._get_plans_sorted(now, window_size_in_days)

        plans = [
            self._create_plan_data(
                plan=p, window_start=window_start, window_end=window_end
            )
            for p in plan_records
        ]
        return Response(
            payout_factor=self.payout_factor_service.calculate_current_payout_factor(),
            window_center=now,
            window_size_in_days=window_size_in_days,
            window_start=window_start,
            window_end=window_end,
            plans=plans,
        )

    def _get_plans_sorted(
        self, now: datetime, window_size_in_days: int
    ) -> list[records.Plan]:
        relevant_plans = list(
            self.database_gateway.get_plans()
            .that_are_approved()
            .that_will_expire_after(now - timedelta(days=window_size_in_days))
        )
        plans_sorted = sorted(
            relevant_plans,
            key=lambda p: (p.approval_date, p.expiration_date),
        )
        return plans_sorted

    def _create_plan_data(
        self, plan: records.Plan, window_start: datetime, window_end: datetime
    ) -> PlanData:
        assert plan.approval_date is not None
        assert plan.expiration_date is not None
        return PlanData(
            id_=plan.id,
            name=plan.prd_name,
            approval_date=plan.approval_date,
            expiration_date=plan.expiration_date,
            is_public_service=plan.is_public_service,
            timeframe=plan.timeframe,
            coverage=self.payout_factor_service.calculate_coverage(
                window_start=window_start,
                window_end=window_end,
                approval=plan.approval_date,
                expiration=plan.expiration_date,
            ),
        )
