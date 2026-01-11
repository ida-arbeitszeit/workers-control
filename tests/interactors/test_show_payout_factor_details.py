from datetime import datetime, timedelta

from parameterized import parameterized

from tests.interactors.base_test_case import BaseTestCase
from tests.payout_factor import PayoutFactorConfigTestImpl
from workers_control.core.interactors import show_payout_factor_details
from workers_control.core.services.payout_factor import PayoutFactorService


class InteractorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(
            show_payout_factor_details.ShowPayoutFactorDetailsInteractor
        )
        self.payout_factor_config = self.injector.get(PayoutFactorConfigTestImpl)
        self.payout_factor_service = self.injector.get(PayoutFactorService)

    def test_that_current_payout_factor_is_shown(self) -> None:
        response = self.interactor.show_payout_factor_details()
        assert (
            response.payout_factor
            == self.payout_factor_service.calculate_current_payout_factor()
        )

    @parameterized.expand((datetime(2020, 5, 1), datetime(2025, 1, 9)))
    def test_that_current_time_is_shown_as_window_center(self, dt: datetime) -> None:
        self.datetime_service.freeze_time(dt)
        response = self.interactor.show_payout_factor_details()
        self.datetime_service.advance_time()
        assert response.window_center == dt

    @parameterized.expand((2, 100))
    def test_that_configured_window_size_is_shown(self, size: int) -> None:
        self.payout_factor_config.set_window_length(size)
        response = self.interactor.show_payout_factor_details()
        assert response.window_size_in_days == size

    @parameterized.expand([(datetime(2020, 5, 1), 3), (datetime(2025, 1, 9), 10)])
    def test_that_window_start_is_now_minus_half_window_size(
        self,
        dt: datetime,
        window_size: int,
    ) -> None:
        self.datetime_service.freeze_time(dt)
        self.payout_factor_config.set_window_length(window_size)
        response = self.interactor.show_payout_factor_details()
        expected_start = dt - timedelta(days=window_size / 2)
        assert response.window_start == expected_start

    @parameterized.expand([(datetime(2020, 5, 1), 4), (datetime(2025, 1, 9), 20)])
    def test_that_window_end_is_now_plus_half_window_size(
        self,
        dt: datetime,
        window_size: int,
    ) -> None:
        self.datetime_service.freeze_time(dt)
        self.payout_factor_config.set_window_length(window_size)
        response = self.interactor.show_payout_factor_details()
        expected_end = dt + timedelta(days=window_size / 2)
        assert response.window_end == expected_end


class PlanDataTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(
            show_payout_factor_details.ShowPayoutFactorDetailsInteractor
        )
        self.payout_factor_config = self.injector.get(PayoutFactorConfigTestImpl)

    def test_that_list_of_plans_is_empty_when_there_are_no_plans(self) -> None:
        response = self.interactor.show_payout_factor_details()
        assert not response.plans

    def test_that_unapproved_plan_is_not_listed(self) -> None:
        self.plan_generator.create_plan(approved=False)
        response = self.interactor.show_payout_factor_details()
        assert not response.plans

    def test_that_active_plan_is_listed(self) -> None:
        plan = self.plan_generator.create_plan()
        response = self.interactor.show_payout_factor_details()
        assert len(response.plans) == 1
        assert response.plans[0].id_ == plan

    def test_that_expired_plan_is_listed(self) -> None:
        self.datetime_service.freeze_time(datetime(2020, 2, 1))
        plan = self.plan_generator.create_plan(timeframe=1)
        self.datetime_service.advance_time(timedelta(weeks=1))
        response = self.interactor.show_payout_factor_details()
        assert len(response.plans) == 1
        assert response.plans[0].id_ == plan

    def test_that_plans_are_ordered_by_approval(self) -> None:
        approval_1 = datetime(1901, 1, 1)
        approval_2 = datetime(1902, 1, 1)
        approval_3 = datetime(1903, 1, 1)
        self.datetime_service.freeze_time(approval_1)
        plan_1 = self.plan_generator.create_plan()
        self.datetime_service.freeze_time(approval_2)
        plan_2 = self.plan_generator.create_plan()
        self.datetime_service.freeze_time(approval_3)
        plan_3 = self.plan_generator.create_plan()

        response = self.interactor.show_payout_factor_details()
        assert [p.id_ for p in response.plans] == [plan_1, plan_2, plan_3]

    def test_that_when_plans_have_same_approval_date_they_are_ordered_by_expiration_date(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime(1901, 1, 1))
        plan_1 = self.plan_generator.create_plan(timeframe=1)
        plan_2 = self.plan_generator.create_plan(timeframe=2)
        response = self.interactor.show_payout_factor_details()
        assert [p.id_ for p in response.plans] == [plan_1, plan_2]

    @parameterized.expand((datetime(2020, 5, 1), datetime(2025, 1, 9)))
    def test_that_approval_date_is_set_correctly(
        self,
        approval_date: datetime,
    ) -> None:
        self.datetime_service.freeze_time(approval_date)
        self.plan_generator.create_plan()
        response = self.interactor.show_payout_factor_details()
        assert response.plans[0].approval_date == approval_date

    @parameterized.expand((1, 10, 100))
    def test_that_expiration_date_is_set_correctly(
        self,
        timeframe: int,
    ) -> None:
        approval_date = datetime(2020, 1, 1)
        self.datetime_service.freeze_time(approval_date)
        self.plan_generator.create_plan(timeframe=timeframe)
        response = self.interactor.show_payout_factor_details()
        expected_expiration_date = approval_date + timedelta(days=timeframe)
        assert response.plans[0].expiration_date == expected_expiration_date

    @parameterized.expand((True, False))
    def test_that_is_public_service_is_set_correctly(
        self,
        is_public_service: bool,
    ) -> None:
        self.plan_generator.create_plan(is_public_service=is_public_service)
        response = self.interactor.show_payout_factor_details()
        assert response.plans[0].is_public_service == is_public_service

    @parameterized.expand((7, 30, 90))
    def test_that_timeframe_is_set_correctly(
        self,
        timeframe: int,
    ) -> None:
        self.plan_generator.create_plan(timeframe=timeframe)
        response = self.interactor.show_payout_factor_details()
        assert response.plans[0].timeframe == timeframe

    def test_that_plan_coverage_is_shown(self) -> None:
        self.plan_generator.create_plan()
        response = self.interactor.show_payout_factor_details()
        assert response.plans[0].coverage is not None
