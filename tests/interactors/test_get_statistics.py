from datetime import timedelta
from decimal import Decimal
from typing import Union

from parameterized import parameterized

from tests.datetime_service import datetime_utc
from tests.interactors.base_test_case import BaseTestCase
from workers_control.core.interactors.get_statistics import GetStatisticsInteractor
from workers_control.core.records import ProductionCosts

Number = Union[int, Decimal]


def production_costs(p: Number, r: Number, a: Number) -> ProductionCosts:
    return ProductionCosts(
        labour_cost=Decimal(a),
        means_cost=Decimal(p),
        resource_cost=Decimal(r),
    )


class StatisticsBaseTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(GetStatisticsInteractor)


class CountCompaniesTests(StatisticsBaseTestCase):
    @parameterized.expand(
        [
            (0,),
            (1,),
            (2,),
        ]
    )
    def test_that_companies_are_counted(
        self,
        num_companies: int,
    ) -> None:
        for _ in range(num_companies):
            self.company_generator.create_company()
        stats = self.interactor.get_statistics()
        assert stats.registered_companies_count == num_companies


class CountMembersTests(StatisticsBaseTestCase):
    @parameterized.expand(
        [
            (0,),
            (1,),
            (2,),
        ]
    )
    def test_that_number_of_members_is_counted(
        self,
        num_members: int,
    ) -> None:
        for _ in range(num_members):
            self.member_generator.create_member()
        stats = self.interactor.get_statistics()
        assert stats.registered_members_count == num_members


class CountCooperationsTests(StatisticsBaseTestCase):
    @parameterized.expand(
        [
            (0,),
            (1,),
            (2,),
        ]
    )
    def test_that_number_of_cooperations_is_counted(
        self,
        num_cooperations: int,
    ) -> None:
        for _ in range(num_cooperations):
            self.cooperation_generator.create_cooperation()
        stats = self.interactor.get_statistics()
        assert stats.cooperations_count == num_cooperations


class CountActivePlansTests(StatisticsBaseTestCase):
    def test_all_active_plans_are_counted(self) -> None:
        self.plan_generator.create_plan()
        self.plan_generator.create_plan()
        self.plan_generator.create_plan(
            is_public_service=True,
        )
        stats = self.interactor.get_statistics()
        assert stats.active_plans_count == 3

    def test_that_expired_plans_are_ignored(self) -> None:
        now = datetime_utc(2000, 1, 1)
        self.datetime_service.freeze_time(now)
        self.plan_generator.create_plan(
            timeframe=1,
        )
        self.plan_generator.create_plan(
            timeframe=1,
            is_public_service=True,
        )
        self.datetime_service.advance_time(
            timedelta(days=2),
        )
        stats = self.interactor.get_statistics()
        assert stats.active_plans_count == 0


class CountActivePublicPlansTests(StatisticsBaseTestCase):
    def test_that_all_active_and_public_plans_are_counted(self) -> None:
        self.plan_generator.create_plan(
            is_public_service=True,
        )
        self.plan_generator.create_plan(
            is_public_service=True,
        )
        stats = self.interactor.get_statistics()
        assert stats.active_plans_public_count == 2

    def test_that_productive_plans_are_ignored(
        self,
    ) -> None:
        self.plan_generator.create_plan(
            is_public_service=False,
        )
        stats = self.interactor.get_statistics()
        assert stats.active_plans_public_count == 0

    def test_that_expired_public_plans_are_ignored(
        self,
    ) -> None:
        now = datetime_utc(2000, 1, 1)
        self.datetime_service.freeze_time(now)
        self.plan_generator.create_plan(
            is_public_service=True,
            timeframe=1,
        )
        self.datetime_service.advance_time(
            timedelta(days=2),
        )
        stats = self.interactor.get_statistics()
        assert stats.active_plans_public_count == 0


class CalculateAverageTimeframeTests(StatisticsBaseTestCase):
    def test_average_calculation_of_two_active_plan_timeframes(self) -> None:
        self.plan_generator.create_plan(timeframe=3)
        self.plan_generator.create_plan(timeframe=7)
        stats = self.interactor.get_statistics()
        assert stats.avg_timeframe == 5


class CalculatePlannedWorkTests(StatisticsBaseTestCase):
    def test_adding_up_planned_labour_of_two_plans(self) -> None:
        PLANNED_LABOUR_PLAN_1 = 3
        self.plan_generator.create_plan(
            costs=production_costs(1, 1, PLANNED_LABOUR_PLAN_1),
        )
        PLANNED_LABOUR_PLAN_2 = 2
        self.plan_generator.create_plan(
            costs=production_costs(1, 1, PLANNED_LABOUR_PLAN_2),
        )
        stats = self.interactor.get_statistics()
        assert stats.planned_work == PLANNED_LABOUR_PLAN_1 + PLANNED_LABOUR_PLAN_2

    def test_adding_up_resources_of_two_plans(self) -> None:
        PLANNED_RESOURCES_PLAN_1 = 3
        self.plan_generator.create_plan(
            costs=production_costs(1, PLANNED_RESOURCES_PLAN_1, 1),
        )
        PLANNED_RESOURCES_PLAN_2 = 2
        self.plan_generator.create_plan(
            costs=production_costs(1, PLANNED_RESOURCES_PLAN_2, 1),
        )
        stats = self.interactor.get_statistics()
        assert (
            stats.planned_resources
            == PLANNED_RESOURCES_PLAN_1 + PLANNED_RESOURCES_PLAN_2
        )

    def test_adding_up_means_of_two_plans(self) -> None:
        PLANNED_MEANS_PLAN_1 = 3
        self.plan_generator.create_plan(
            costs=production_costs(PLANNED_MEANS_PLAN_1, 1, 1),
        )
        PLANNED_MEANS_PLAN_2 = 2
        self.plan_generator.create_plan(
            costs=production_costs(PLANNED_MEANS_PLAN_2, 1, 1),
        )
        stats = self.interactor.get_statistics()
        assert stats.planned_means == PLANNED_MEANS_PLAN_1 + PLANNED_MEANS_PLAN_2


class CalculatePayoutFactorTests(StatisticsBaseTestCase):
    def test_that_payout_factor_is_available_even_without_plans_in_economy(
        self,
    ) -> None:
        stats = self.interactor.get_statistics()
        assert stats.payout_factor is not None


class CalculatePsfBalanceTests(StatisticsBaseTestCase):
    def test_that_psf_balance_is_available_even_without_plans_in_economy(
        self,
    ) -> None:
        stats = self.interactor.get_statistics()
        assert stats.psf_balance is not None
