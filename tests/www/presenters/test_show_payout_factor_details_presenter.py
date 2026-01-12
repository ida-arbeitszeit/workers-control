from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

from parameterized import parameterized

from tests.datetime_service import datetime_min_utc
from tests.www.base_test_case import BaseTestCase
from workers_control.core.interactors.show_payout_factor_details import (
    PlanData,
    Response,
)
from workers_control.web.www.presenters.show_payout_factor_details_presenter import (
    ShowPayoutFactorDetailsPresenter,
)


class PresenterBaseTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ShowPayoutFactorDetailsPresenter)

    def _create_response(
        self,
        payout_factor: Decimal = Decimal("1.0"),
        window_center: datetime | None = None,
        window_size_in_days: int = 30,
        window_start: datetime | None = None,
        window_end: datetime | None = None,
        plans: list[PlanData] | None = None,
    ) -> Response:
        if window_center is None:
            window_center = datetime_min_utc()
        if window_start is None:
            window_start = datetime_min_utc()
        if window_end is None:
            window_end = datetime_min_utc() + timedelta(days=window_size_in_days)
        if plans is None:
            plans = []
        return Response(
            payout_factor=payout_factor,
            window_center=window_center,
            window_size_in_days=window_size_in_days,
            window_start=window_start,
            window_end=window_end,
            plans=plans,
        )


class ShowPayoutFactorDetailsPresenterTests(PresenterBaseTestCase):
    def test_payout_factor_is_formatted_as_string(self) -> None:
        response = self._create_response(payout_factor=Decimal("1.5"))
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.payout_factor, "1.50")

    def test_payout_factor_is_rounded_to_2_decimal_places(self) -> None:
        response = self._create_response(payout_factor=Decimal("0.74567"))
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.payout_factor, "0.75")

    def test_window_size_in_days_is_formatted_as_string(self) -> None:
        response = self._create_response(window_size_in_days=30)
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.window_size_in_days, "30")

    def test_window_start_is_formatted_using_datetime_formatter(self) -> None:
        window_start = datetime_min_utc()
        response = self._create_response(window_start=window_start)
        view_model = self.presenter.present(response)
        expected = self.datetime_formatter.format_datetime(window_start)
        self.assertEqual(view_model.window_start, expected)

    def test_window_end_is_formatted_using_datetime_formatter(self) -> None:
        window_end = datetime_min_utc() + timedelta(days=30)
        response = self._create_response(window_end=window_end)
        view_model = self.presenter.present(response)
        expected = self.datetime_formatter.format_datetime(window_end)
        self.assertEqual(view_model.window_end, expected)

    def test_window_start_and_end_are_formatted_correctly(self) -> None:
        window_start = datetime_min_utc()
        window_end = datetime_min_utc() + timedelta(days=60)
        response = self._create_response(
            window_start=window_start,
            window_end=window_end,
        )
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.window_start,
            self.datetime_formatter.format_datetime(window_start),
        )
        self.assertEqual(
            view_model.window_end,
            self.datetime_formatter.format_datetime(window_end),
        )

    def test_that_correct_plot_url_is_shown(self) -> None:
        response = self._create_response()
        view_model = self.presenter.present(response)
        expected = self.url_index.get_payout_factor_details_bar_plot_url()
        assert view_model.plot_url == expected


class PlanRowsTests(PresenterBaseTestCase):
    @parameterized.expand(
        [
            (0,),
            (1,),
            (5,),
        ]
    )
    def test_that_number_of_plan_rows_matches_number_of_plans(
        self,
        number_of_plans: int,
    ) -> None:
        plans = [self._create_plan_data() for _ in range(number_of_plans)]
        response = self._create_response(plans=plans)
        view_model = self.presenter.present(response)
        assert len(view_model.plans) == len(plans)

    def test_that_row_index_starts_with_zero(self) -> None:
        expected_indices = ["0", "1", "2"]
        plans = [self._create_plan_data() for _ in range(3)]
        response = self._create_response(plans=plans)
        view_model = self.presenter.present(response)
        actual_indices = [plan.row_index for plan in view_model.plans]
        assert actual_indices == expected_indices

    @parameterized.expand(
        [
            ("Short Plan Name",),
            ("This is a plan name that is definitely longer than thirty characters",),
        ]
    )
    def test_that_plan_name_is_shortened_correctly(self, plan_name: str) -> None:
        plan = self._create_plan_data(name=plan_name)
        response = self._create_response(plans=[plan])
        view_model = self.presenter.present(response)
        assert view_model.plans[0].shortened_plan_name == plan_name[:30]

    def test_that_plan_url_is_generated_correctly(self) -> None:
        plan = self._create_plan_data()
        response = self._create_response(plans=[plan])
        view_model = self.presenter.present(response)
        user_role = self.session.get_user_role()
        expected_url = self.url_index.get_plan_details_url(
            user_role=user_role,
            plan_id=plan.id_,
        )
        assert view_model.plans[0].plan_url == expected_url

    @parameterized.expand(
        [
            (True,),
            (False,),
        ]
    )
    def test_that_is_public_is_passed_correctly(
        self,
        is_public_service: bool,
    ) -> None:
        plan = self._create_plan_data(is_public_service=is_public_service)
        response = self._create_response(plans=[plan])
        view_model = self.presenter.present(response)
        assert view_model.plans[0].is_public == is_public_service

    @parameterized.expand(
        [
            (Decimal("-0.25"), "-25%"),
            (Decimal("0.0"), "0%"),
            (Decimal("0.25"), "25%"),
            (Decimal("0.5"), "50%"),
            (Decimal("0.75"), "75%"),
            (Decimal("1.0"), "100%"),
            (Decimal("1.5"), "150%"),
        ]
    )
    def test_that_decimal_coverage_is_converted_into_percentage_string(
        self, coverage: Decimal, expected_string: str
    ) -> None:
        plan = self._create_plan_data(coverage=coverage)
        response = self._create_response(plans=[plan])
        view_model = self.presenter.present(response)
        assert view_model.plans[0].coverage == expected_string

    def _create_plan_data(
        self,
        id_: UUID | None = None,
        name: str = "Example Plan Name",
        approval_date: datetime | None = None,
        expiration_date: datetime | None = None,
        is_public_service: bool = True,
        timeframe: int = 30,
        coverage: Decimal = Decimal("0.5"),
    ) -> PlanData:
        if id_ is None:
            id_ = uuid4()
        if approval_date is None:
            approval_date = datetime_min_utc()
        if expiration_date is None:
            expiration_date = approval_date + timedelta(days=timeframe)
        return PlanData(
            id_=id_,
            name=name,
            approval_date=approval_date,
            expiration_date=expiration_date,
            is_public_service=is_public_service,
            timeframe=timeframe,
            coverage=coverage,
        )


class NavbarTests(PresenterBaseTestCase):
    def test_navbar_items_contain_global_statistics_and_payout_factor_details(
        self,
    ) -> None:
        response = self._create_response()
        view_model = self.presenter.present(response)
        assert len(view_model.navbar_items) == 2
        assert view_model.navbar_items[0].text == self.translator.gettext(
            "Global statistics"
        )
        assert (
            view_model.navbar_items[0].url == self.url_index.get_global_statistics_url()
        )
        assert view_model.navbar_items[1].text == self.translator.gettext(
            "Payout Factor Details"
        )
        assert view_model.navbar_items[1].url is None
