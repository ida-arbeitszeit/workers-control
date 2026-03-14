from dataclasses import dataclass
from datetime import UTC, datetime, tzinfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from flask import current_app, request

from workers_control.core.datetime_service import DatetimeService
from workers_control.web.formatters.datetime_formatter import TimezoneConfiguration


class RealtimeDatetimeService(DatetimeService):
    def now(self) -> datetime:
        return datetime.now(UTC)


@dataclass
class FlaskDatetimeFormatter:
    timezone_config: TimezoneConfiguration

    def format_datetime(
        self,
        date: datetime,
        fmt: str | None = None,
    ) -> str:
        tz = self.timezone_config.get_timezone_of_current_user()
        date = date.astimezone(tz)
        if fmt is None:
            fmt = "%d.%m.%Y %H:%M"
        return date.strftime(fmt)


class FlaskTimezoneConfiguration:
    def get_timezone_of_current_user(self) -> tzinfo:
        user_timezone = request.cookies.get("user_timezone")
        if user_timezone:
            try:
                return ZoneInfo(user_timezone)
            except (ZoneInfoNotFoundError, TypeError, KeyError):
                pass
        default_timezone = current_app.config.get("DEFAULT_USER_TIMEZONE", "UTC")
        try:
            zone_info = ZoneInfo(default_timezone)
        except (ZoneInfoNotFoundError, TypeError):
            return UTC
        return zone_info
