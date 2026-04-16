"""Core clock logic shared by the GUI application."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, tzinfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DEFAULT_DATE_FORMAT = "iso"
DEFAULT_DISPLAY_MODE = "digital"
DEFAULT_TIMEZONE_NAME = "Local"
LOCAL_TIMEZONE_NAME = "Local"
DISPLAY_MODES = ("digital", "analogue")
ALARM_REPEAT_MODES = ("daily", "once")
COMMON_TIMEZONE_NAMES = (
    LOCAL_TIMEZONE_NAME,
    "UTC",
    "Africa/Lagos",
    "Europe/London",
    "America/New_York",
)
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


def _validate_display_mode(display_mode: str) -> str:
    if display_mode not in DISPLAY_MODES:
        raise ValueError("display_mode must be 'digital' or 'analogue'")
    return display_mode


def _validate_alarm_repeat_mode(repeat_mode: str) -> str:
    if repeat_mode not in ALARM_REPEAT_MODES:
        raise ValueError("repeat_mode must be 'daily' or 'once'")
    return repeat_mode


def _get_local_timezone() -> tzinfo:
    return datetime.now().astimezone().tzinfo or ZoneInfo("UTC")


def resolve_timezone(timezone_name: str = DEFAULT_TIMEZONE_NAME) -> tzinfo:
    """Resolve a supported timezone name into a tzinfo object."""

    normalized_name = _validate_timezone_name(timezone_name)
    if normalized_name == LOCAL_TIMEZONE_NAME:
        return _get_local_timezone()
    return ZoneInfo(normalized_name)


def _validate_timezone_name(timezone_name: str) -> str:
    if not isinstance(timezone_name, str) or not timezone_name.strip():
        raise ValueError("timezone_name must be a non-empty string")

    normalized_name = timezone_name.strip()
    if normalized_name == LOCAL_TIMEZONE_NAME:
        return normalized_name

    try:
        ZoneInfo(normalized_name)
    except ZoneInfoNotFoundError as exc:
        raise ValueError("timezone_name must be a valid IANA timezone") from exc

    return normalized_name


@dataclass(slots=True)
class AlarmConfig:
    """Configuration for a single alarm entry."""

    hour: int
    minute: int
    label: str = ""
    repeat_mode: str = "daily"
    enabled: bool = True

    def __post_init__(self) -> None:
        self.hour = int(self.hour)
        self.minute = int(self.minute)
        if not 0 <= self.hour <= 23:
            raise ValueError("hour must be between 0 and 23")
        if not 0 <= self.minute <= 59:
            raise ValueError("minute must be between 0 and 59")
        self.label = str(self.label).strip()
        self.repeat_mode = _validate_alarm_repeat_mode(self.repeat_mode)
        self.enabled = bool(self.enabled)


@dataclass(slots=True, frozen=True)
class AlarmEvent:
    """A single alarm firing event."""

    index: int
    alarm: AlarmConfig
    triggered_at: datetime


@dataclass(slots=True, frozen=True)
class AnalogueClockData:
    """Precomputed hand angles for an analogue clock face."""

    hour_angle: float
    minute_angle: float
    second_angle: float | None


def _validate_alarms(alarms: list[AlarmConfig]) -> list[AlarmConfig]:
    normalized_alarms: list[AlarmConfig] = []
    for alarm in alarms:
        if not isinstance(alarm, AlarmConfig):
            raise ValueError("alarms must contain AlarmConfig items")
        normalized_alarms.append(alarm)
    return normalized_alarms


@dataclass(slots=True)
class ClockSettings:
    """Configuration shared by the clock application."""

    time_format: int = 24
    show_date: bool = False
    date_format: str = DEFAULT_DATE_FORMAT
    display_mode: str = DEFAULT_DISPLAY_MODE
    show_seconds: bool = True
    timezone_name: str = DEFAULT_TIMEZONE_NAME
    alarms: list[AlarmConfig] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.time_format = _validate_time_format(self.time_format)
        self.show_date = bool(self.show_date)
        self.date_format = _validate_date_format(self.date_format)
        self.display_mode = _validate_display_mode(self.display_mode)
        self.show_seconds = bool(self.show_seconds)
        self.timezone_name = _validate_timezone_name(self.timezone_name)
        self.alarms = _validate_alarms(list(self.alarms))


def get_current_datetime(timezone_name: str = DEFAULT_TIMEZONE_NAME) -> datetime:
    """Return the current local or selected timezone-aware system time."""

    resolved_timezone = resolve_timezone(timezone_name)
    if timezone_name == LOCAL_TIMEZONE_NAME:
        return datetime.now().astimezone(resolved_timezone)
    return datetime.now(resolved_timezone)


def normalize_datetime(
    current_time: datetime,
    timezone_name: str = DEFAULT_TIMEZONE_NAME,
) -> datetime:
    """Convert aware datetimes into the selected timezone.

    Naive datetimes are left untouched so tests and explicit sample moments can
    stay simple and deterministic.
    """

    _validate_timezone_name(timezone_name)
    if current_time.tzinfo is None:
        return current_time
    return current_time.astimezone(resolve_timezone(timezone_name))


def format_time(
    current_time: datetime,
    time_format: int = 24,
    show_seconds: bool = True,
    timezone_name: str = DEFAULT_TIMEZONE_NAME,
) -> str:
    """Format a datetime into a 12-hour or 24-hour clock string."""

    normalized_format = _validate_time_format(time_format)
    moment = normalize_datetime(current_time, timezone_name)
    if normalized_format == 24:
        return moment.strftime("%H:%M:%S" if show_seconds else "%H:%M")
    return moment.strftime("%I:%M:%S %p" if show_seconds else "%I:%M %p")


def format_date(
    current_time: datetime,
    date_format: str = DEFAULT_DATE_FORMAT,
    timezone_name: str = DEFAULT_TIMEZONE_NAME,
) -> str:
    """Format a datetime into one of the supported calendar date styles."""

    normalized_format = _validate_date_format(date_format)
    moment = normalize_datetime(current_time, timezone_name)
    return moment.strftime(DATE_FORMAT_PATTERNS[normalized_format])


def build_display_parts(
    current_time: datetime,
    settings: ClockSettings,
) -> tuple[str, str]:
    """Build the display strings for the current settings."""

    time_text = format_time(
        current_time,
        settings.time_format,
        settings.show_seconds,
        settings.timezone_name,
    )
    if not settings.show_date:
        return time_text, ""
    return time_text, format_date(
        current_time,
        settings.date_format,
        settings.timezone_name,
    )


def build_display_string(current_time: datetime, settings: ClockSettings) -> str:
    """Build the full display text for the current settings."""

    time_text, date_text = build_display_parts(current_time, settings)
    if not date_text:
        return time_text
    return f"{time_text}\n{date_text}"


def build_analogue_clock_data(
    current_time: datetime,
    show_seconds: bool = True,
    timezone_name: str = DEFAULT_TIMEZONE_NAME,
) -> AnalogueClockData:
    """Build the angles for an analogue clock face."""

    moment = normalize_datetime(current_time, timezone_name)
    second = moment.second
    minute = moment.minute + (second / 60)
    hour = (moment.hour % 12) + (minute / 60)

    hour_angle = hour * 30
    minute_angle = minute * 6
    second_angle = second * 6 if show_seconds else None

    return AnalogueClockData(
        hour_angle=hour_angle,
        minute_angle=minute_angle,
        second_angle=second_angle,
    )


def format_alarm_summary(alarm: AlarmConfig) -> str:
    """Return a compact summary for list rendering."""

    repeat_label = "Daily" if alarm.repeat_mode == "daily" else "Once"
    enabled_label = "On" if alarm.enabled else "Off"
    suffix = f" - {alarm.label}" if alarm.label else ""
    return (
        f"{alarm.hour:02d}:{alarm.minute:02d}{suffix} "
        f"({repeat_label}, {enabled_label})"
    )


class ClockController:
    """Stateful wrapper around settings, formatting, and alarms."""

    def __init__(self, settings: ClockSettings | None = None) -> None:
        self.settings = settings or ClockSettings()
        self._last_triggered_alarm_tokens: dict[int, tuple[int, int, int, int, int]] = {}

    def _clear_alarm_runtime_state(self) -> None:
        self._last_triggered_alarm_tokens.clear()

    def set_time_format(self, time_format: int) -> None:
        self.settings.time_format = _validate_time_format(time_format)

    def set_show_date(self, show_date: bool) -> None:
        self.settings.show_date = bool(show_date)

    def set_date_format(self, date_format: str) -> None:
        self.settings.date_format = _validate_date_format(date_format)

    def set_display_mode(self, display_mode: str) -> None:
        self.settings.display_mode = _validate_display_mode(display_mode)

    def set_show_seconds(self, show_seconds: bool) -> None:
        self.settings.show_seconds = bool(show_seconds)

    def set_timezone_name(self, timezone_name: str) -> None:
        self.settings.timezone_name = _validate_timezone_name(timezone_name)
        self._clear_alarm_runtime_state()

    def set_alarms(self, alarms: list[AlarmConfig]) -> None:
        self.settings.alarms = _validate_alarms(list(alarms))
        self._clear_alarm_runtime_state()

    def add_alarm(self, alarm: AlarmConfig) -> None:
        if not isinstance(alarm, AlarmConfig):
            raise ValueError("alarm must be an AlarmConfig")
        self.settings.alarms.append(alarm)
        self._clear_alarm_runtime_state()

    def update_alarm(self, index: int, alarm: AlarmConfig) -> None:
        if not isinstance(alarm, AlarmConfig):
            raise ValueError("alarm must be an AlarmConfig")
        self.settings.alarms[index] = alarm
        self._clear_alarm_runtime_state()

    def delete_alarm(self, index: int) -> None:
        del self.settings.alarms[index]
        self._clear_alarm_runtime_state()

    def toggle_alarm_enabled(self, index: int) -> bool:
        self.settings.alarms[index].enabled = not self.settings.alarms[index].enabled
        self._clear_alarm_runtime_state()
        return self.settings.alarms[index].enabled

    def toggle_show_date(self) -> bool:
        self.settings.show_date = not self.settings.show_date
        return self.settings.show_date

    def get_display_datetime(self, current_time: datetime | None = None) -> datetime:
        if current_time is None:
            return get_current_datetime(self.settings.timezone_name)
        return normalize_datetime(current_time, self.settings.timezone_name)

    def get_display_parts(
        self,
        current_time: datetime | None = None,
    ) -> tuple[str, str]:
        moment = self.get_display_datetime(current_time)
        return build_display_parts(moment, self.settings)

    def get_display_text(self, current_time: datetime | None = None) -> str:
        moment = self.get_display_datetime(current_time)
        return build_display_string(moment, self.settings)

    def get_analogue_clock_data(
        self,
        current_time: datetime | None = None,
    ) -> AnalogueClockData:
        moment = self.get_display_datetime(current_time)
        return build_analogue_clock_data(
            moment,
            self.settings.show_seconds,
            self.settings.timezone_name,
        )

    def check_alarms(self, current_time: datetime | None = None) -> list[AlarmEvent]:
        """Return any alarms that should fire for the given moment."""

        moment = self.get_display_datetime(current_time)
        minute_token = (
            moment.year,
            moment.month,
            moment.day,
            moment.hour,
            moment.minute,
        )
        fired_events: list[AlarmEvent] = []

        for index, alarm in enumerate(self.settings.alarms):
            if not alarm.enabled:
                continue
            if alarm.hour != moment.hour or alarm.minute != moment.minute:
                continue
            if self._last_triggered_alarm_tokens.get(index) == minute_token:
                continue

            self._last_triggered_alarm_tokens[index] = minute_token
            fired_events.append(
                AlarmEvent(
                    index=index,
                    alarm=replace(alarm),
                    triggered_at=moment,
                )
            )

            if alarm.repeat_mode == "once":
                alarm.enabled = False

        return fired_events
