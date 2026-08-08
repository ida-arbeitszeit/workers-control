from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import matplotlib.dates as mdates
from matplotlib.axes import Axes
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.colors import to_rgba
from matplotlib.figure import Figure
from matplotlib.patches import Patch
from parameterized import parameterized

from tests.base_test_case import BaseTestCase
from tests.datetime_service import datetime_utc
from workers_control.core.interactors.show_payout_factor_details import (
    BasicServiceConsumptionData,
    PlanData,
    Response,
)
from workers_control.flask.plotter import GeneralPlotter, PayoutFactorDetailsPlotter
from workers_control.web.colors import HexColors

PNG_MAGIC_BYTES = b"\x89PNG"


class PlotterTestCase(BaseTestCase):
    def render(self, figure: Figure) -> Axes:
        # Ticks are only calculated and labelled once the figure is drawn.
        FigureCanvasAgg(figure).draw()
        return figure.axes[0]

    def get_tick_labels(self, axes: Axes) -> list[str]:
        return [tick.get_text() for tick in axes.get_xticklabels()]

    def get_y_tick_labels(self, axes: Axes) -> list[str]:
        return [tick.get_text() for tick in axes.get_yticklabels()]

    def get_legend_labels(self, axes: Axes) -> list[str]:
        legend = axes.get_legend()
        assert legend
        return [text.get_text() for text in legend.get_texts()]

    def get_ticks_in_user_timezone(self, axes: Axes) -> list[datetime]:
        tz = self.timezone_configuration.get_timezone_of_current_user()
        return [mdates.num2date(tick, tz=tz) for tick in axes.get_xticks()]


class GeneralPlotterTests(PlotterTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.plotter = self.injector.get(GeneralPlotter)

    def test_that_line_plot_is_rendered_as_png(self) -> None:
        png = self.plotter.create_line_plot(
            x=[datetime_utc(2026, 8, 4), datetime_utc(2026, 8, 6)],
            y=[Decimal(1), Decimal(5)],
        )
        assert png.startswith(PNG_MAGIC_BYTES)

    def test_that_days_are_labelled_in_utc_for_a_user_in_utc(self) -> None:
        self.timezone_configuration.set_timezone_of_current_user("UTC")
        axes = self.render(self.create_two_day_figure())
        assert set(self.get_tick_labels(axes)) == {
            "2026-08-04",
            "2026-08-05",
            "2026-08-06",
        }

    def test_that_days_are_labelled_in_local_time_for_a_user_in_tokyo(self) -> None:
        self.timezone_configuration.set_timezone_of_current_user("Asia/Tokyo")
        axes = self.render(self.create_two_day_figure())
        assert set(self.get_tick_labels(axes)) == {
            "2026-08-05",
            "2026-08-06",
            "2026-08-07",
        }

    @parameterized.expand([("UTC",), ("Asia/Tokyo",), ("America/New_York",)])
    def test_that_daily_ticks_fall_on_midnight_in_the_users_timezone(
        self, timezone: str
    ) -> None:
        self.timezone_configuration.set_timezone_of_current_user(timezone)
        figure = self.plotter._create_line_plot_figure(
            x=[datetime_utc(2026, 8, 4, 20), datetime_utc(2026, 8, 14, 20)],
            y=[Decimal(1), Decimal(5)],
        )
        axes = self.render(figure)
        ticks = self.get_ticks_in_user_timezone(axes)
        assert ticks
        for tick in ticks:
            assert (tick.hour, tick.minute) == (0, 0)

    def test_that_bar_plot_is_rendered_as_png(self) -> None:
        png = self.plotter.create_bar_plot(
            x_coordinates=["a", "b"],
            height_of_bars=[Decimal(1), Decimal(3)],
            colors_of_bars=["red", "blue"],
            fig_size=(5, 4),
            y_label="Amount",
        )
        assert png.startswith(PNG_MAGIC_BYTES)

    def test_that_bar_plot_y_axis_is_labelled_with_fractions_by_default(self) -> None:
        axes = self.render(self.create_bar_plot_figure(integer_y_ticks=False))
        assert any("." in label for label in self.get_y_tick_labels(axes))

    def test_that_bar_plot_y_axis_is_labelled_with_whole_numbers_if_requested(
        self,
    ) -> None:
        axes = self.render(self.create_bar_plot_figure(integer_y_ticks=True))
        labels = self.get_y_tick_labels(axes)
        assert labels
        for label in labels:
            assert label.lstrip("\N{MINUS SIGN}-").isdigit()

    def create_bar_plot_figure(self, integer_y_ticks: bool) -> Figure:
        # Two bars of height 1 and 3 make matplotlib pick fractional ticks
        # unless integer ticks are requested.
        return self.plotter._create_bar_plot_figure(
            x_coordinates=["a", "b"],
            height_of_bars=[Decimal(1), Decimal(3)],
            colors_of_bars=["red", "blue"],
            fig_size=(5, 4),
            y_label="Amount",
            integer_y_ticks=integer_y_ticks,
        )

    def create_two_day_figure(self) -> Figure:
        # In Tokyo (UTC+9) both timestamps fall on the following day.
        return self.plotter._create_line_plot_figure(
            x=[datetime_utc(2026, 8, 4, 20), datetime_utc(2026, 8, 6, 20)],
            y=[Decimal(1), Decimal(5)],
        )


class PayoutFactorDetailsPlotterTests(PlotterTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.plotter = self.injector.get(PayoutFactorDetailsPlotter)
        self.colors = self.injector.get(HexColors)

    def test_that_plot_is_rendered_as_png(self) -> None:
        png = self.plotter.plot(
            self.create_response(
                plans=[
                    self.create_plan(),
                    self.create_plan(is_public_service=True),
                ],
                basic_service_consumptions=[self.create_basic_service_consumption()],
            )
        )
        assert png.startswith(PNG_MAGIC_BYTES)

    def test_that_plot_without_plans_or_consumptions_is_rendered_as_png(self) -> None:
        png = self.plotter.plot(self.create_response())
        assert png.startswith(PNG_MAGIC_BYTES)

    @parameterized.expand([("UTC",), ("Asia/Tokyo",), ("America/New_York",)])
    def test_that_month_ticks_fall_on_the_first_of_the_month_in_the_users_timezone(
        self, timezone: str
    ) -> None:
        self.timezone_configuration.set_timezone_of_current_user(timezone)
        figure = self.plotter._create_figure(self.create_response())
        axes = self.render(figure)
        ticks = self.get_ticks_in_user_timezone(axes)
        assert ticks
        for tick in ticks:
            assert (tick.day, tick.hour, tick.minute) == (1, 0, 0)

    @parameterized.expand([("UTC",), ("Asia/Tokyo",), ("America/New_York",)])
    def test_that_ticks_are_labelled_with_their_month_in_the_users_timezone(
        self, timezone: str
    ) -> None:
        self.timezone_configuration.set_timezone_of_current_user(timezone)
        figure = self.plotter._create_figure(self.create_response())
        axes = self.render(figure)
        ticks = self.get_ticks_in_user_timezone(axes)
        labels = self.get_tick_labels(axes)
        assert ticks
        for tick, label in zip(ticks, labels, strict=True):
            assert label == tick.strftime("%Y-%m")

    def test_that_y_axis_is_labelled_with_plan_indices_only_and_ignores_basic_services(
        self,
    ) -> None:
        figure = self.plotter._create_figure(
            self.create_response(
                plans=[self.create_plan(), self.create_plan()],
                basic_service_consumptions=[self.create_basic_service_consumption()],
            )
        )
        axes = self.render(figure)
        assert self.get_y_tick_labels(axes) == ["0", "1"]

    def test_that_legend_lists_both_plan_types(self) -> None:
        figure = self.plotter._create_figure(
            self.create_response(
                plans=[
                    self.create_plan(),
                    self.create_plan(is_public_service=True),
                ]
            )
        )
        axes = self.render(figure)
        labels = self.get_legend_labels(axes)
        assert self.translator.gettext("Public plans") in labels
        assert self.translator.gettext("Productive plans") in labels

    def test_that_legend_lists_both_plan_types_even_without_any_plans(self) -> None:
        figure = self.plotter._create_figure(self.create_response())
        axes = self.render(figure)
        labels = self.get_legend_labels(axes)
        assert self.translator.gettext("Public plans") in labels
        assert self.translator.gettext("Productive plans") in labels

    @parameterized.expand(
        [
            ("Public plans", "warning"),
            ("Productive plans", "primary"),
        ]
    )
    def test_that_legend_entry_has_the_color_of_the_bars_it_describes(
        self, label: str, color_name: str
    ) -> None:
        figure = self.plotter._create_figure(
            self.create_response(
                plans=[
                    self.create_plan(),
                    self.create_plan(is_public_service=True),
                ]
            )
        )
        axes = self.render(figure)
        expected_color = getattr(self.colors, color_name)
        legend_entry = self.translator.gettext(label)
        assert self.get_legend_color(axes, legend_entry) == to_rgba(expected_color)

    def get_legend_color(self, axes: Axes, label: str) -> tuple[float, ...]:
        legend = axes.get_legend()
        assert legend
        handles = dict(zip(self.get_legend_labels(axes), legend.legend_handles))
        handle = handles[label]
        assert isinstance(handle, Patch)
        return to_rgba(handle.get_facecolor())

    def create_response(
        self,
        plans: list[PlanData] | None = None,
        basic_service_consumptions: list[BasicServiceConsumptionData] | None = None,
    ) -> Response:
        window_size_in_days = 90
        center = datetime_utc(2026, 8, 5, 12)
        return Response(
            payout_factor=Decimal("1.0"),
            window_center=center,
            window_size_in_days=window_size_in_days,
            window_start=center - timedelta(days=window_size_in_days / 2),
            window_end=center + timedelta(days=window_size_in_days / 2),
            display_start=center - timedelta(days=window_size_in_days),
            display_end=center + timedelta(days=window_size_in_days),
            plans=plans if plans is not None else [],
            basic_service_consumptions=(
                basic_service_consumptions
                if basic_service_consumptions is not None
                else []
            ),
        )

    def create_plan(self, is_public_service: bool = False) -> PlanData:
        return PlanData(
            id_=uuid4(),
            name="test plan",
            approval_date=datetime_utc(2026, 7, 5),
            expiration_date=datetime_utc(2026, 9, 5),
            is_public_service=is_public_service,
            timeframe=62,
            coverage=Decimal("1.0"),
        )

    def create_basic_service_consumption(self) -> BasicServiceConsumptionData:
        return BasicServiceConsumptionData(
            date=datetime_utc(2026, 8, 1),
            value=Decimal(10),
        )
