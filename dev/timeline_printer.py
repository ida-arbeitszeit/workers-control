from datetime import datetime, timedelta
from decimal import Decimal

from workers_control.core.interactors import show_payout_factor_details
from workers_control.core.services.payout_factor import PayoutFactorService

SCREEN_WIDTH = 70


class PayoutFactorWindowCLIPrinter:
    """
    Renders an ASCII visualization of plans on a timeline, relative to a gliding
    payout factor calculation window.
    """

    def __init__(
        self,
        interactor: show_payout_factor_details.ShowPayoutFactorDetailsInteractor,
    ) -> None:
        self.interactor = interactor
        self.response = self.interactor.show_payout_factor_details()
        self._timeline_start, self._timeline_end = self._calculate_timeline_bounds()

    def _calculate_timeline_bounds(self) -> tuple[datetime, datetime]:
        """Calculate the timeline bounds to include all plans and the window."""
        start = self.response.window_start
        end = self.response.window_end
        for plan in self.response.plans:
            start = min(start, plan.approval_date)
            end = max(end, plan.expiration_date)
        # Ensure we have at least 1 day range
        if start >= end:
            end = start + timedelta(days=1)
        return start, end

    def render_timeline(self) -> str:
        lines = []
        lines.append("")
        lines.append("Payout Factor (FIC) Gliding Window")
        lines.append("==================================")
        lines.append("")
        lines.extend(self._render_timeline_info())
        lines.append("")
        lines.extend(self._render_window_info())
        lines.append("")
        lines.append(self._render_graphical_window_line())

        if not self.response.plans:
            lines.append("  (no plans)")
        else:
            graphical_plan_lines = []
            textual_plan_lines = []
            for i, plan in enumerate(self.response.plans):
                graphical_plan_lines.append(self._render_graphical_plan_line(plan, i))
                textual_plan_lines.append(self._render_textual_plan_line(plan, i))
            lines.extend(graphical_plan_lines)
            lines.append("")
            lines.extend(textual_plan_lines)

        return "\n".join(lines)

    def _render_window_info(self) -> list[str]:
        return [
            "Gliding window:",
            f"  Center: {self.response.window_center.date()} (now)",
            f"  Size: {self.response.window_size_in_days} days",
            f"  Start: {self.response.window_start.date()}",
            f"  End: {self.response.window_end.date()}",
        ]

    def _render_timeline_info(self) -> list[str]:
        return [
            "Timeline:",
            f"  Start: {self._timeline_start.date()}",
            f"  End: {self._timeline_end.date()}",
        ]

    def _render_graphical_window_line(self) -> str:
        """Render the window line: ---[----N----]---"""
        line = ["-"] * SCREEN_WIDTH
        left_pos = self._date_to_pos(self.response.window_start)
        right_pos = self._date_to_pos(self.response.window_end)
        now_pos = self._date_to_pos(self.response.window_center)

        if 0 <= left_pos < SCREEN_WIDTH:
            line[left_pos] = "["
        if 0 <= right_pos < SCREEN_WIDTH:
            line[right_pos] = "]"
        if 0 <= now_pos < SCREEN_WIDTH:
            line[now_pos] = "N"

        return f"    {''.join(line)}  <- window (N=now)"

    def _render_graphical_plan_line(
        self,
        plan: show_payout_factor_details.PlanData,
        index: int,
    ) -> str:
        """Render the plan line: -----****----- or -----oooo-----"""
        line = ["-"] * SCREEN_WIDTH
        start_pos = self._date_to_pos(plan.approval_date)
        end_pos = self._date_to_pos(plan.expiration_date)

        if plan.is_public_service:
            marker = "\033[93mo\033[0m"  # Yellow circle
        else:
            marker = "*"  # Normal asterisk for productive

        for i in range(max(0, start_pos), min(SCREEN_WIDTH, end_pos + 1)):
            line[i] = marker

        return f"    {''.join(line)} ({index})"

    def _date_to_pos(self, date: datetime) -> int:
        """Convert a date to a position on the screen."""
        timeline_range = (self._timeline_end - self._timeline_start).days
        if timeline_range <= 0:
            timeline_range = 1
        days_from_start = (date - self._timeline_start).days
        return int((days_from_start / timeline_range) * (SCREEN_WIDTH - 1))

    def _calculate_coverage(self, plan: show_payout_factor_details.PlanData) -> Decimal:
        return PayoutFactorService.calculate_coverage(
            self.response.window_start,
            self.response.window_end,
            plan.approval_date,
            plan.expiration_date,
        )

    def _render_textual_plan_line(
        self, plan: show_payout_factor_details.PlanData, index: int
    ) -> str:
        coverage = self._calculate_coverage(plan)
        cov_str = f"{coverage * 100:.0f}%"

        return (
            f"({index}) "
            f"id={str(plan.id_)[:8]} "
            f"type={'publ' if plan.is_public_service else 'prod'} "
            f"tf={plan.timeframe}d "
            f"appr={plan.approval_date.date()} "
            f"exp={plan.expiration_date.date()} "
            f"cov={cov_str}"
        )
