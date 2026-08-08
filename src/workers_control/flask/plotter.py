import io
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple, Union

import matplotlib.dates as mdates
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator

from workers_control.core.interactors import show_payout_factor_details
from workers_control.web.colors import HexColors
from workers_control.web.formatters.datetime_formatter import TimezoneConfiguration
from workers_control.web.translator import Translator

DEFAULT_LINE_PLOT_SIZE: Tuple[int, int] = (10, 5)


@dataclass
class GeneralPlotter:
    timezone_config: TimezoneConfiguration

    def create_line_plot(
        self,
        x: List[datetime],
        y: List[Decimal],
        fig_size: Tuple[int, int] = DEFAULT_LINE_PLOT_SIZE,
    ) -> bytes:
        fig = self._create_line_plot_figure(x=x, y=y, fig_size=fig_size)
        return self._figure_to_bytes(fig)

    def _create_line_plot_figure(
        self,
        x: List[datetime],
        y: List[Decimal],
        fig_size: Tuple[int, int] = DEFAULT_LINE_PLOT_SIZE,
    ) -> Figure:
        tz = self.timezone_config.get_timezone_of_current_user()
        fig = Figure()
        ax = fig.subplots()
        ax.axhline(linestyle="--", color="black")
        ax.plot(x, y)  # type: ignore[arg-type]
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d", tz=tz))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(tz=tz))
        fig.set_size_inches(fig_size[0], fig_size[1])
        fig.autofmt_xdate()
        return fig

    def create_bar_plot(
        self,
        x_coordinates: List[Union[int, str]],
        height_of_bars: List[Decimal],
        colors_of_bars: List[str],
        fig_size: Tuple[int, int],
        y_label: Optional[str],
        integer_y_ticks: bool = False,
    ) -> bytes:
        fig = self._create_bar_plot_figure(
            x_coordinates=x_coordinates,
            height_of_bars=height_of_bars,
            colors_of_bars=colors_of_bars,
            fig_size=fig_size,
            y_label=y_label,
            integer_y_ticks=integer_y_ticks,
        )
        return self._figure_to_bytes(fig)

    def _create_bar_plot_figure(
        self,
        x_coordinates: List[Union[int, str]],
        height_of_bars: List[Decimal],
        colors_of_bars: List[str],
        fig_size: Tuple[int, int],
        y_label: Optional[str],
        integer_y_ticks: bool = False,
    ) -> Figure:
        fig = Figure()
        ax = fig.subplots()
        ax.bar(x_coordinates, height_of_bars, color=colors_of_bars)  # type: ignore[arg-type]
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        if y_label:
            ax.set_ylabel(y_label)
        if integer_y_ticks:
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        fig.set_size_inches(fig_size[0], fig_size[1])
        return fig

    def _figure_to_bytes(self, fig: Figure) -> bytes:
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return output.getvalue()


@dataclass
class PayoutFactorDetailsPlotter:
    translator: Translator
    colors: HexColors
    timezone_config: TimezoneConfiguration

    def plot(self, response: show_payout_factor_details.Response) -> bytes:
        fig = self._create_figure(response)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=0.5)
        buf.seek(0)
        return buf.getvalue()

    def _create_figure(self, response: show_payout_factor_details.Response) -> Figure:
        tz = self.timezone_config.get_timezone_of_current_user()

        public_color = self.colors.warning
        productive_color = self.colors.primary

        plan_indices: list[int] = []
        start: list[datetime] = []
        end: list[datetime] = []
        colors_list: list[str] = []

        for i, p in enumerate(response.plans):
            plan_indices.append(i)
            start.append(p.approval_date)
            end.append(p.expiration_date)
            colors_list.append(
                public_color if p.is_public_service else productive_color
            )

        plan_durations = [(e - s).days for s, e in zip(start, end)]
        bs_row_y = -1

        fig = Figure()
        ax = fig.add_subplot(1, 1, 1)

        ax.barh(
            plan_indices,
            plan_durations,
            left=[mdates.date2num(s) for s in start],
            color=colors_list,
        )
        bs_label = self.translator.gettext("Basic services")
        bs_dates = [
            mdates.date2num(c.date) for c in response.basic_service_consumptions
        ]
        ax.scatter(
            bs_dates,
            [bs_row_y] * len(bs_dates),
            marker="*",
            s=80,
            color=self.colors.success,
            label=bs_label,
            zorder=3,
        )
        ax.set_yticks(plan_indices)

        title = self.translator.gettext("Payout Factor Calculation Window")
        ax.set_title(title)
        ylabel = self.translator.gettext("Plans")
        ax.set_ylabel(ylabel)

        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m", tz=tz))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(tz=tz))
        fig.autofmt_xdate()
        ax.invert_yaxis()
        ax.grid(axis="x", linestyle="--", alpha=0.6)

        ax.axvspan(
            mdates.date2num(response.window_start),
            mdates.date2num(response.window_end),
            alpha=0.25,
            color=self.colors.danger,
            label=self.translator.gettext("Calculation window"),
        )
        ax.axvline(
            mdates.date2num(response.window_center),
            linestyle="--",
            linewidth=1,
            label=self.translator.gettext("Now"),
        )
        plan_type_handles = [
            Patch(color=public_color, label=self.translator.gettext("Public plans")),
            Patch(
                color=productive_color,
                label=self.translator.gettext("Productive plans"),
            ),
        ]
        handles, _ = ax.get_legend_handles_labels()
        ax.legend(handles=plan_type_handles + handles)
        fig.set_size_inches(14, (len(plan_indices) + 1) * 0.3 + 2)

        ax.set_xlim(
            mdates.date2num(response.display_start),
            mdates.date2num(response.display_end),
        )
        return fig
