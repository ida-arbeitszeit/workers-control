from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

from workers_control.core import records
from workers_control.core.datetime_service import DatetimeService
from workers_control.core.repositories import DatabaseGateway
from workers_control.core.services.payout_factor import PayoutFactorConfig


@dataclass
class Response:
    window_center: datetime
    window_size_in_days: int
    window_start: datetime
    window_end: datetime
    plans: list[PlanData]


@dataclass
class PlanData:
    id_: UUID
    approval_date: datetime
    expiration_date: datetime
    is_public_service: bool
    timeframe: int


@dataclass
class ShowPayoutFactorWindowDetailsInteractor:
    payout_factor_config: PayoutFactorConfig
    datetime_service: DatetimeService
    database_gateway: DatabaseGateway

    def show_payout_factor_window_details(self) -> Response:
        window_size_in_days = self.payout_factor_config.get_window_length_in_days()
        now = self.datetime_service.now()
        plans = self._get_approved_plans_sorted()
        return Response(
            window_center=now,
            window_size_in_days=window_size_in_days,
            window_start=now - timedelta(days=window_size_in_days / 2),
            window_end=now + timedelta(days=window_size_in_days / 2),
            plans=plans,
        )

    def _get_approved_plans_sorted(self) -> list[PlanData]:
        plans_unsorted = list(self.database_gateway.get_plans().that_are_approved())
        plans_sorted = sorted(
            plans_unsorted,
            key=lambda p: (p.approval_date, p.expiration_date),
        )
        return [self._create_plan_data(p) for p in plans_sorted]

    def _create_plan_data(self, plan: records.Plan) -> PlanData:
        assert plan.approval_date is not None
        assert plan.expiration_date is not None
        return PlanData(
            id_=plan.id,
            approval_date=plan.approval_date,
            expiration_date=plan.expiration_date,
            is_public_service=plan.is_public_service,
            timeframe=plan.timeframe,
        )
