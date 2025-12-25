from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from arbeitszeit import records


def _days_between(a: datetime, b: datetime) -> int:
    """Calculate the number of days between two datetimes."""
    return (a - b).days


@dataclass
class PlanTimelineData:
    plan: records.Plan
    approval_offset_left: int | None
    expiry_offset_left: int | None
    approval_offset_right: int | None
    expiry_offset_right: int | None
    coverage: float | None

    @classmethod
    def from_plan(
        cls,
        plan: records.Plan,
        left_border: datetime,
        right_border: datetime,
    ) -> PlanTimelineData:
        """Create PlanTimelineData from a plan and window borders."""
        approval = plan.approval_date
        expiry = plan.expiration_date

        # Calculate coverage: fraction of plan's duration inside the window
        coverage: float | None = None
        if approval and expiry:
            coverage_start = max(approval, left_border)
            coverage_end = min(expiry, right_border)
            plan_duration_days = (expiry - approval).days
            covered_days = max(0, (coverage_end - coverage_start).days)
            coverage = (
                covered_days / plan_duration_days if plan_duration_days > 0 else 0.0
            )

        return cls(
            plan=plan,
            approval_offset_left=(
                _days_between(approval, left_border) if approval else None
            ),
            expiry_offset_left=_days_between(expiry, left_border) if expiry else None,
            approval_offset_right=(
                _days_between(approval, right_border) if approval else None
            ),
            expiry_offset_right=_days_between(expiry, right_border) if expiry else None,
            coverage=coverage,
        )


class TimelinePrinter:
    """
    Prints an ASCII visualization of plans on a timeline, relative to a gliding
    fic calculation window.
    """

    def __init__(
        self,
        now: datetime,
        plans: list[records.Plan],
        window_size: int,
        total_width: int = 70,
    ) -> None:
        self._now = now
        self._window_size = window_size
        self._total_width = total_width
        self._left_border = now - (timedelta(days=window_size) / 2)
        self._right_border = now + (timedelta(days=window_size) / 2)

        # Sort plans and compute timeline data
        self._plans = sorted(
            plans,
            key=lambda p: (
                p.approval_date or p.plan_creation_date,
                p.expiration_date or p.approval_date or p.plan_creation_date,
            ),
        )
        self._plan_data = [
            PlanTimelineData.from_plan(p, self._left_border, self._right_border)
            for p in self._plans
        ]
        self._min_day, self._max_day = self._calculate_extent()

    def render(self) -> str:
        """Render the timeline visualization to a string."""
        lines = [
            f"Window (FIC):  [{self._left_border.date()} .. {self._right_border.date()}]  "
            f"size={self._window_size} days  now={self._now.date()}",
            self._render_window_line(),
        ]

        if not self._plan_data:
            lines.append("  (no plans)")
        else:
            for i, data in enumerate(self._plan_data):
                lines.append(self._render_plan_line(data, i))
            lines.append("")
            for i, data in enumerate(self._plan_data):
                lines.append(self._render_plan_info(data, i))

        return "\n".join(lines)

    def print_timeline(self) -> None:
        """Print the timeline visualization to stdout."""
        print(self.render())

    def _calculate_extent(self) -> tuple[int, int]:
        """Calculate the min and max day positions across all plans."""
        min_day = 0
        max_day = self._window_size

        for data in self._plan_data:
            if data.approval_offset_left is not None:
                min_day = min(min_day, data.approval_offset_left)
            if data.expiry_offset_left is not None:
                max_day = max(max_day, data.expiry_offset_left)

        return min_day, max_day

    def _day_to_pos(self, day: int) -> int:
        """Convert a day (relative to left border) to a character position."""
        total_days = self._max_day - self._min_day
        if total_days <= 0:
            total_days = 1
        return int((day - self._min_day) / total_days * (self._total_width - 1))

    def _render_window_line(self) -> str:
        """Render the window line: ---[----N----]---"""
        line = ["-"] * self._total_width
        left_pos = self._day_to_pos(0)
        right_pos = self._day_to_pos(self._window_size)
        now_pos = self._day_to_pos(self._window_size // 2)

        if 0 <= left_pos < self._total_width:
            line[left_pos] = "["
        if 0 <= right_pos < self._total_width:
            line[right_pos] = "]"
        if 0 <= now_pos < self._total_width:
            line[now_pos] = "N"

        return f"    {''.join(line)}  <- window (N=now)"

    def _render_plan_line(self, data: PlanTimelineData, index: int) -> str:
        """Render the plan line: -----****----- or -----oooo----- (yellow for public)."""
        if data.approval_offset_left is None or data.expiry_offset_left is None:
            return "    (missing date info for ASCII graph)"

        line = ["-"] * self._total_width
        start_pos = self._day_to_pos(data.approval_offset_left)
        end_pos = self._day_to_pos(data.expiry_offset_left)

        # Use * for productive plans, yellow o for public plans
        if data.plan.is_public_service:
            marker = "\033[93mo\033[0m"  # Yellow circle
        else:
            marker = "*"  # Normal asterisk for productive

        for i in range(max(0, start_pos), min(self._total_width, end_pos + 1)):
            line[i] = marker

        return f"    {''.join(line)} ({index})"

    def _render_plan_info(self, data: PlanTimelineData, index: int) -> str:
        """Render plan info line."""
        plan = data.plan
        approval = plan.approval_date
        expiry = plan.expiration_date
        cov_str = f"{data.coverage * 100:.0f}%" if data.coverage is not None else "—"

        return (
            f"({index}) "
            f"id={str(plan.id)[:8]} "
            f"type={'publ' if plan.is_public_service else 'prod'} "
            f"tf={plan.timeframe}d "
            f"appr={approval.date() if approval else '—'} "
            f"exp={expiry.date() if expiry else '—'} "
            f"cov={cov_str}"
        )
