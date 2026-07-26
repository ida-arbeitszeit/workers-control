from datetime import datetime, timedelta
from decimal import Decimal
from typing import Callable
from uuid import uuid4

from parameterized import parameterized

from tests.datetime_service import datetime_utc
from workers_control.core.interactors.get_draft_details import (
    DraftDetailsResponse,
    DraftDetailsSuccess,
    GetDraftDetailsInteractor,
)
from workers_control.core.records import ProductionCosts

from .base_test_case import BaseTestCase


class GetDraftDetailsInteractorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.get_draft_details = self.injector.get(GetDraftDetailsInteractor)

    def test_that_correct_planner_id_is_returned(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        draft = self.plan_generator.draft_plan(planner=planner)
        details = self.get_draft_details.execute(draft)
        assert_success(details, lambda s: s.planner_id == planner)

    def test_that_correct_production_costs_are_shown(self) -> None:
        draft = self.plan_generator.draft_plan(
            costs=ProductionCosts(
                means_cost=Decimal(1),
                labour_cost=Decimal(2),
                resource_cost=Decimal(3),
            )
        )
        details = self.get_draft_details.execute(draft)
        assert_success(
            details,
            lambda s: all(
                [
                    s.means_cost == Decimal(1),
                    s.labour_cost == Decimal(2),
                    s.resources_cost == Decimal(3),
                ]
            ),
        )

    def test_that_correct_product_name_is_shown(self) -> None:
        draft = self.plan_generator.draft_plan(product_name="test product")
        details = self.get_draft_details.execute(draft)
        assert_success(details, lambda s: s.product_name == "test product")

    def test_that_correct_product_description_is_shown(self) -> None:
        draft = self.plan_generator.draft_plan(description="test description")
        details = self.get_draft_details.execute(draft)
        assert_success(details, lambda s: s.description == "test description")

    def test_that_correct_product_unit_is_shown(self) -> None:
        draft = self.plan_generator.draft_plan(production_unit="test unit")
        details = self.get_draft_details.execute(draft)
        assert_success(details, lambda s: s.production_unit == "test unit")

    def test_that_correct_amount_is_shown(self) -> None:
        draft = self.plan_generator.draft_plan(amount=123)
        details = self.get_draft_details.execute(draft)
        assert_success(details, lambda s: s.amount == 123)

    def test_that_correct_public_service_is_shown(self) -> None:
        draft = self.plan_generator.draft_plan(is_public_service=True)
        details = self.get_draft_details.execute(draft)
        assert_success(details, lambda s: s.is_public_service == True)

    def test_that_none_is_returned_when_draft_does_not_exist(self) -> None:
        assert self.get_draft_details.execute(uuid4()) is None

    @parameterized.expand(
        [
            (datetime_utc(2000, 1, 2),),
            (datetime_utc(2039, 1, 3),),
        ]
    )
    def test_that_creation_timestamp_is_time_of_request_1(
        self, expected_timestamp: datetime
    ) -> None:
        self.datetime_service.freeze_time(expected_timestamp)
        draft = self.plan_generator.draft_plan(is_public_service=True)
        self.datetime_service.advance_time(timedelta(days=1))
        details = self.get_draft_details.execute(draft)
        assert_success(details, lambda s: s.creation_timestamp == expected_timestamp)


def assert_success(
    response: DraftDetailsResponse, assertion: Callable[[DraftDetailsSuccess], bool]
) -> None:
    assert isinstance(response, DraftDetailsSuccess)
    assert assertion(response)
