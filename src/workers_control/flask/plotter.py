import io
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple, Union

import matplotlib.dates as mdates
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from workers_control.core.interactors import show_payout_factor_details
from workers_control.web.colors import HexColors
from workers_control.web.formatters.datetime_formatter import TimezoneConfiguration
from workers_control.web.translator import Translator


class GeneralPlotter:
    def create_line_plot(
        self, x: List[datetime], y: List[Decimal], fig_size: Tuple[int, int] = (10, 5)
    ) -> bytes:
        fig = Figure()
        ax = fig.subplots()
        ax.axhline(linestyle="--", color="black")
        ax.plot(x, y)  # type: ignore[arg-type]
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        fig.set_size_inches(fig_size[0], fig_size[1])
        fig.autofmt_xdate()
        return self._figure_to_bytes(fig)

    def create_bar_plot(
        self,
        x_coordinates: List[Union[int, str]],
        height_of_bars: List[Decimal],
        colors_of_bars: List[str],
        fig_size: Tuple[int, int],
        y_label: Optional[str],
    ) -> bytes:
        fig = Figure()
        ax = fig.subplots()
        ax.bar(x_coordinates, height_of_bars, color=colors_of_bars)  # type: ignore[arg-type]
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        if y_label:
            ax.set_ylabel(y_label)
        fig.set_size_inches(fig_size[0], fig_size[1])
        return self._figure_to_bytes(fig)

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

        plans: list[str] = []
        start: list[datetime] = []
        end: list[datetime] = []
        colors_list: list[str] = []

        for i, p in enumerate(response.plans):
            plans.append(f"{i}")
            start.append(p.approval_date)
            end.append(p.expiration_date)
            if p.is_public_service:
                colors_list.append(self.colors.warning)
            else:
                colors_list.append(self.colors.primary)

        plan_durations = [(e - s).days for s, e in zip(start, end)]

        fig = Figure()
        ax = fig.add_subplot(1, 1, 1)

        ax.barh(
            plans,
            plan_durations,
            left=[mdates.date2num(s) for s in start],
            color=colors_list,
        )
        title = self.translator.gettext("Payout Factor Calculation Window")
        ax.set_title(title)
        ylabel = self.translator.gettext("Plans")
        ax.set_ylabel(ylabel)

        tz = self.timezone_config.get_timezone_of_current_user()
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d", tz=tz))
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
        ax.legend()
        fig.set_size_inches(14, len(plans) * 0.3 + 2)

        margin = timedelta(days=response.window_size_in_days / 2)
        ax.set_xlim(
            mdates.date2num(response.window_start - margin),
            mdates.date2num(response.window_end + margin),
        )

        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=0.5)
        buf.seek(0)
        return buf.getvalue()
