from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

from parameterized import parameterized
from pytest import approx

from tests.datetime_service import datetime_utc
from workers_control.core.interactors.approve_plan import ApprovePlanInteractor
from workers_control.core.interactors.get_plan_details import (
    GetPlanDetailsInteractor,
    PlanDetails,
)
from workers_control.core.records import ProductionCosts

from .base_test_case import BaseTestCase


class InteractorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(GetPlanDetailsInteractor)
        self.approve_plan_interactor = self.injector.get(ApprovePlanInteractor)
        self.company = self.company_generator.create_company_record()

    def test_that_none_is_returned_when_plan_does_not_exist(self) -> None:
        request = GetPlanDetailsInteractor.Request(uuid4())
        self.assertFalse(self.interactor.get_plan_details(request))

    def test_plan_details_is_returned_when_plan_exists(self) -> None:
        plan = self.plan_generator.create_plan()
        request = GetPlanDetailsInteractor.Request(plan)
        self.assertTrue(self.interactor.get_plan_details(request))

    def test_that_correct_plan_id_is_shown(self) -> None:
        plan = self.plan_generator.create_plan()
        self.assertEqual(self.get_details(plan).plan_id, plan)

    def test_that_correct_planner_name_is_shown(self) -> None:
        planner = self.company_generator.create_company_record()
        plan = self.plan_generator.create_plan(planner=planner.id)
        self.assertEqual(self.get_details(plan).planner_name, planner.name)

    def test_that_correct_active_status_is_shown_when_plan_is_active(self) -> None:
        plan = self.plan_generator.create_plan()
        self.assertTrue(self.get_details(plan).is_active)

    def test_that_correct_production_costs_are_shown(self) -> None:
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(
                means_cost=Decimal(1),
                labour_cost=Decimal(2),
                resource_cost=Decimal(3),
            )
        )
        details = self.get_details(plan)
        self.assertEqual(details.means_cost, Decimal(1))
        self.assertEqual(details.labour_cost, Decimal(2))
        self.assertEqual(details.resources_cost, Decimal(3))

    @parameterized.expand(
        [
            (True, False),
            (False, True),
            (True, True),
            (False, False),
        ]
    )
    def test_that_correct_cost_per_unit_is_shown(
        self, is_public_service: bool, approved: bool
    ) -> None:
        plan = self.plan_generator.create_plan(
            is_public_service=is_public_service,
            amount=2,
            approved=approved,
            costs=ProductionCosts(
                means_cost=Decimal(1),
                labour_cost=Decimal(2),
                resource_cost=Decimal(3),
            ),
        )
        self.assertEqual(self.get_details(plan).cost_per_unit, Decimal(3))

    @parameterized.expand(
        [
            ("test product name",),
            ("another product name",),
        ]
    )
    def test_that_correct_product_name_is_shown(
        self, expected_product_name: str
    ) -> None:
        plan = self.plan_generator.create_plan(product_name=expected_product_name)
        assert self.get_details(plan).product_name == expected_product_name

    @parameterized.expand(
        [
            ("test description",),
            ("another description",),
        ]
    )
    def test_that_correct_product_description_is_shown(
        self, expected_description: str
    ) -> None:
        plan = self.plan_generator.create_plan(description=expected_description)
        assert self.get_details(plan).description == expected_description

    @parameterized.expand(
        [
            ("test unit",),
            ("another test unit",),
        ]
    )
    def test_that_correct_product_unit_is_shown(self, expected_unit: str) -> None:
        plan = self.plan_generator.create_plan(production_unit=expected_unit)
        assert self.get_details(plan).production_unit == expected_unit

    def test_that_correct_amount_is_shown(self) -> None:
        plan = self.plan_generator.create_plan(amount=123)
        self.assertEqual(self.get_details(plan).amount, 123)

    def test_that_correct_public_service_is_shown(self) -> None:
        plan = self.plan_generator.create_plan(is_public_service=True)
        self.assertTrue(self.get_details(plan).is_public_service)

    def test_that_no_cooperation_is_shown_when_plan_is_not_cooperating(self) -> None:
        plan = self.plan_generator.create_plan(cooperation=None)
        details = self.get_details(plan)
        self.assertFalse(details.is_cooperating)
        self.assertIsNone(details.cooperation)

    def test_that_correct_cooperation_is_shown(self) -> None:
        coop = self.cooperation_generator.create_cooperation()
        plan = self.plan_generator.create_plan(cooperation=coop)
        details = self.get_details(plan)
        self.assertTrue(details.is_cooperating)
        self.assertEqual(details.cooperation, coop)

    def test_that_zero_active_days_is_shown_if_plan_is_not_active_yet(self) -> None:
        plan = self.plan_generator.create_plan(approved=False)
        self.assertEqual(self.get_details(plan).active_days, 0)

    def test_that_zero_active_days_is_shown_if_plan_is_active_since_less_than_one_day(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        self.assertEqual(self.get_details(plan).active_days, 0)

    def test_that_one_active_days_is_shown_if_plan_is_active_since_25_hours(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        plan = self.plan_generator.create_plan()
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 2, hour=1))
        self.assertEqual(self.get_details(plan).active_days, 1)

    def test_that_a_plans_timeframe_is_shown_as_active_days_if_plan_is_expired(
        self,
    ) -> None:
        timeframe = 7
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        plan = self.plan_generator.create_plan(timeframe=timeframe)
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 11))
        self.assertEqual(self.get_details(plan).active_days, timeframe)

    @parameterized.expand(
        [
            (datetime_utc(2000, 1, 1), timedelta(days=1)),
            (datetime_utc(2001, 2, 2), timedelta(hours=1)),
        ]
    )
    def test_that_creation_date_is_shown(
        self, expected_creation_date: datetime, time_since_creation: timedelta
    ) -> None:
        self.datetime_service.freeze_time(expected_creation_date)
        plan = self.plan_generator.create_plan()
        self.datetime_service.advance_time(time_since_creation)
        self.assertEqual(self.get_details(plan).creation_date, expected_creation_date)

    @parameterized.expand(
        [
            (datetime_utc(2000, 1, 1), timedelta(days=1), timedelta(days=1)),
            (datetime_utc(2001, 2, 2), timedelta(hours=1), timedelta(days=2)),
        ]
    )
    def test_that_approval_date_is_shown_if_it_exists(
        self,
        expected_approval_date: datetime,
        time_between_creation_and_approval: timedelta,
        time_since_approval: timedelta,
    ) -> None:
        self.datetime_service.freeze_time(
            expected_approval_date - time_between_creation_and_approval
        )
        plan = self.plan_generator.create_plan(approved=False)
        self.datetime_service.freeze_time(expected_approval_date)
        self.approve_plan(plan)
        self.datetime_service.advance_time(time_since_approval)
        self.assertEqual(self.get_details(plan).approval_date, expected_approval_date)

    def test_that_expiration_date_is_shown_if_it_exists(self) -> None:
        plan = self.plan_generator.create_plan(timeframe=5)
        self.assertTrue(self.get_details(plan).expiration_date)

    @parameterized.expand(
        [
            (Decimal(10), 10, 10, Decimal(20), 5, 1, Decimal(2.5)),  # avg(1, 4) = 2.5
            (
                Decimal(310),
                20,
                90,
                Decimal(25),
                5,
                45,
                Decimal(10.25),
            ),  # avg(15.5, 5) = 10.25
        ]
    )
    def test_that_two_productive_plans_with_different_timeframes_return_correct_coop_price(
        self,
        costs_plan1: Decimal,
        amount_plan1: int,
        timeframe_plan1: int,
        costs_plan2: Decimal,
        amount_plan2: int,
        timeframe_plan2: int,
        expected_coop_price: Decimal,
    ) -> None:
        cooperation = self.cooperation_generator.create_cooperation()
        self.plan_generator.create_plan(
            cooperation=cooperation,
            costs=ProductionCosts(costs_plan1, Decimal(0), Decimal(0)),
            amount=amount_plan1,
            timeframe=timeframe_plan1,
        )
        plan = self.plan_generator.create_plan(
            cooperation=cooperation,
            costs=ProductionCosts(costs_plan2, Decimal(0), Decimal(0)),
            amount=amount_plan2,
            timeframe=timeframe_plan2,
        )
        response = self.interactor.get_plan_details(
            GetPlanDetailsInteractor.Request(plan_id=plan)
        )
        assert response
        self.assertEqual(response.plan_details.price_per_unit, expected_coop_price)

    def test_that_cooperative_prices_are_calculated_by_averaging_plan_prices(
        self,
    ) -> None:
        @dataclass
        class TestExample:
            plan_a_costs: Decimal
            plan_b_costs: Decimal
            expected_cooperative_costs: Decimal

        examples = [
            TestExample(
                plan_a_costs=Decimal(5),
                plan_b_costs=Decimal(15),
                expected_cooperative_costs=Decimal(10),
            ),
            TestExample(
                plan_a_costs=Decimal(3),
                plan_b_costs=Decimal(5),
                expected_cooperative_costs=Decimal(4),
            ),
        ]
        for example in examples:
            coop = self.cooperation_generator.create_cooperation()
            self.plan_generator.create_plan(
                cooperation=coop,
                costs=self.create_production_costs(total_costs=example.plan_a_costs),
                amount=1,
            )
            plan = self.plan_generator.create_plan(
                cooperation=coop,
                costs=self.create_production_costs(total_costs=example.plan_b_costs),
                amount=1,
            )
            response = self.interactor.get_plan_details(
                GetPlanDetailsInteractor.Request(plan_id=plan)
            )
            assert response
            assert response.plan_details.price_per_unit == approx(
                example.expected_cooperative_costs
            )

    def test_that_indiviual_price_is_calculated_properly(self) -> None:
        @dataclass
        class TestExample:
            total_costs: Decimal
            amount: int
            expected_costs: Decimal

        examples = [
            TestExample(total_costs=Decimal(1), amount=1, expected_costs=Decimal(1)),
            TestExample(total_costs=Decimal(3), amount=1, expected_costs=Decimal(3)),
            TestExample(total_costs=Decimal(3), amount=3, expected_costs=Decimal(1)),
        ]
        for example in examples:
            plan = self.plan_generator.create_plan(
                costs=self.create_production_costs(total_costs=example.total_costs),
                amount=example.amount,
            )
            response = self.interactor.get_plan_details(
                GetPlanDetailsInteractor.Request(plan_id=plan)
            )
            assert response
            assert response.plan_details.price_per_unit == approx(
                example.expected_costs
            )

    def test_that_individual_price_for_public_plan_is_0(self) -> None:
        plan = self.plan_generator.create_plan(
            costs=self.create_production_costs(total_costs=Decimal(10)),
            amount=1,
            is_public_service=True,
        )
        response = self.interactor.get_plan_details(
            GetPlanDetailsInteractor.Request(plan_id=plan)
        )
        assert response
        assert response.plan_details.price_per_unit == Decimal(0)

    def get_details(self, plan_id: UUID) -> PlanDetails:
        response = self.interactor.get_plan_details(
            GetPlanDetailsInteractor.Request(plan_id)
        )
        assert response
        return response.plan_details

    def approve_plan(self, plan: UUID) -> None:
        request = ApprovePlanInteractor.Request(plan=plan)
        response = self.approve_plan_interactor.approve_plan(request)
        assert response.is_plan_approved

    def create_production_costs(
        self, total_costs: Decimal = Decimal(1)
    ) -> ProductionCosts:
        return ProductionCosts(total_costs / 3, total_costs / 3, total_costs / 3)
