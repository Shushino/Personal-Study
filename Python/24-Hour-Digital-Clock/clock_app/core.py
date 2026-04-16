"""Core clock logic shared by all front ends."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


def _validate_time_format(time_format: int) -> int:
    if time_format not in (12, 24):
        raise ValueError("time_format must be 12 or 24")
    return time_format


@dataclass(slots=True)
class ClockSettings:
    """Configuration shared by the console and GUI clocks."""

    time_format: int = 24
    show_date: bool = False

    def __post_init__(self) -> None:
        self.time_format = _validate_time_format(self.time_format)
        self.show_date = bool(self.show_date)


def get_current_datetime() -> datetime:
    """Return the current local system time."""

    return datetime.now()


def format_time(current_time: datetime, time_format: int = 24) -> str:
    """Format a datetime into a 12-hour or 24-hour clock string."""

    normalized_format = _validate_time_format(time_format)
    if normalized_format == 24:
        return current_time.strftime("%H:%M:%S")
    return current_time.strftime("%I:%M:%S %p")


def format_date(current_time: datetime) -> str:
    """Format a datetime into an ISO-like calendar date."""

    return current_time.strftime("%Y-%m-%d")


def build_display_string(current_time: datetime, settings: ClockSettings) -> str:
    """Build the full display text for the current settings."""

    time_text = format_time(current_time, settings.time_format)
    if not settings.show_date:
        return time_text
    return f"{format_date(current_time)} {time_text}"


class ClockController:
    """Small stateful wrapper around clock settings and formatting."""

    def __init__(self, settings: ClockSettings | None = None) -> None:
        self.settings = settings or ClockSettings()

    def set_time_format(self, time_format: int) -> None:
        self.settings.time_format = _validate_time_format(time_format)

    def set_show_date(self, show_date: bool) -> None:
        self.settings.show_date = bool(show_date)

    def toggle_show_date(self) -> bool:
        self.settings.show_date = not self.settings.show_date
        return self.settings.show_date

    def get_display_text(self, current_time: datetime | None = None) -> str:
        moment = current_time or get_current_datetime()
        return build_display_string(moment, self.settings)
