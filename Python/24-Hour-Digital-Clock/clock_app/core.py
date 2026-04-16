"""Core clock logic shared by all front ends."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

DEFAULT_DATE_FORMAT = "iso"
DATE_FORMAT_PATTERNS = {
    "iso": "%Y-%m-%d",
    "dmy_slash": "%d/%m/%Y",
    "long_month": "%B %d, %Y",
}


def _validate_time_format(time_format: int) -> int:
    if time_format not in (12, 24):
        raise ValueError("time_format must be 12 or 24")
    return time_format


def _validate_date_format(date_format: str) -> str:
    if date_format not in DATE_FORMAT_PATTERNS:
        raise ValueError(
            "date_format must be one of: iso, dmy_slash, long_month"
        )
    return date_format


@dataclass(slots=True)
class ClockSettings:
    """Configuration shared by the clock application."""

    time_format: int = 24
    show_date: bool = False
    date_format: str = DEFAULT_DATE_FORMAT

    def __post_init__(self) -> None:
        self.time_format = _validate_time_format(self.time_format)
        self.show_date = bool(self.show_date)
        self.date_format = _validate_date_format(self.date_format)


def get_current_datetime() -> datetime:
    """Return the current local system time."""

    return datetime.now()


def format_time(current_time: datetime, time_format: int = 24) -> str:
    """Format a datetime into a 12-hour or 24-hour clock string."""

    normalized_format = _validate_time_format(time_format)
    if normalized_format == 24:
        return current_time.strftime("%H:%M:%S")
    return current_time.strftime("%I:%M:%S %p")


def format_date(current_time: datetime, date_format: str = DEFAULT_DATE_FORMAT) -> str:
    """Format a datetime into one of the supported calendar date styles."""

    normalized_format = _validate_date_format(date_format)
    return current_time.strftime(DATE_FORMAT_PATTERNS[normalized_format])


def build_display_parts(current_time: datetime, settings: ClockSettings) -> tuple[str, str]:
    """Build the display strings for the current settings."""

    time_text = format_time(current_time, settings.time_format)
    if not settings.show_date:
        return time_text, ""
    return time_text, format_date(current_time, settings.date_format)


def build_display_string(current_time: datetime, settings: ClockSettings) -> str:
    """Build the full display text for the current settings."""

    time_text, date_text = build_display_parts(current_time, settings)
    if not date_text:
        return time_text
    return f"{time_text}\n{date_text}"


class ClockController:
    """Small stateful wrapper around clock settings and formatting."""

    def __init__(self, settings: ClockSettings | None = None) -> None:
        self.settings = settings or ClockSettings()

    def set_time_format(self, time_format: int) -> None:
        self.settings.time_format = _validate_time_format(time_format)

    def set_show_date(self, show_date: bool) -> None:
        self.settings.show_date = bool(show_date)

    def set_date_format(self, date_format: str) -> None:
        self.settings.date_format = _validate_date_format(date_format)

    def toggle_show_date(self) -> bool:
        self.settings.show_date = not self.settings.show_date
        return self.settings.show_date

    def get_display_parts(
        self, current_time: datetime | None = None
    ) -> tuple[str, str]:
        moment = current_time or get_current_datetime()
        return build_display_parts(moment, self.settings)

    def get_display_text(self, current_time: datetime | None = None) -> str:
        moment = current_time or get_current_datetime()
        return build_display_string(moment, self.settings)
