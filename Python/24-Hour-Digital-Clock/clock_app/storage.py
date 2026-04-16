"""Persistence helpers for the GUI clock settings."""

from __future__ import annotations

import json
import os
from pathlib import Path

from .core import (
    AlarmConfig,
    ClockSettings,
    DEFAULT_DATE_FORMAT,
    DEFAULT_DISPLAY_MODE,
    DEFAULT_TIMEZONE_NAME,
    _validate_date_format,
    _validate_display_mode,
    _validate_time_format,
    _validate_timezone_name,
)

APP_DIRECTORY_NAME = "24-Hour-Digital-Clock"
SETTINGS_FILE_NAME = "settings.json"


def _default_local_appdata() -> Path:
    return Path.home() / "AppData" / "Local"


def get_settings_path() -> Path:
    """Return the path where GUI settings are stored."""

    base_directory = Path(os.environ.get("LOCALAPPDATA", _default_local_appdata()))
    return base_directory / APP_DIRECTORY_NAME / SETTINGS_FILE_NAME


def _load_alarm(raw_alarm: object) -> AlarmConfig | None:
    if not isinstance(raw_alarm, dict):
        return None

    label = raw_alarm.get("label", "")
    repeat_mode = raw_alarm.get("repeat_mode", "daily")
    enabled = raw_alarm.get("enabled", True)

    if not isinstance(label, str):
        return None
    if not isinstance(repeat_mode, str):
        return None
    if not isinstance(enabled, bool):
        return None

    try:
        return AlarmConfig(
            hour=int(raw_alarm["hour"]),
            minute=int(raw_alarm["minute"]),
            label=label,
            repeat_mode=repeat_mode,
            enabled=enabled,
        )
    except (KeyError, TypeError, ValueError):
        return None


def load_settings() -> ClockSettings:
    """Load persisted settings and fall back to defaults on any error."""

    settings_path = get_settings_path()

    try:
        raw_payload = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ClockSettings()

    if not isinstance(raw_payload, dict):
        return ClockSettings()

    time_format = 24
    raw_time_format = raw_payload.get("time_format", time_format)
    try:
        time_format = _validate_time_format(int(raw_time_format))
    except (TypeError, ValueError):
        time_format = 24

    show_date = raw_payload.get("show_date", False)
    if not isinstance(show_date, bool):
        show_date = False

    date_format = raw_payload.get("date_format", DEFAULT_DATE_FORMAT)
    if isinstance(date_format, str):
        try:
            date_format = _validate_date_format(date_format)
        except ValueError:
            date_format = DEFAULT_DATE_FORMAT
    else:
        date_format = DEFAULT_DATE_FORMAT

    display_mode = raw_payload.get("display_mode", DEFAULT_DISPLAY_MODE)
    if isinstance(display_mode, str):
        try:
            display_mode = _validate_display_mode(display_mode)
        except ValueError:
            display_mode = DEFAULT_DISPLAY_MODE
    else:
        display_mode = DEFAULT_DISPLAY_MODE

    show_seconds = raw_payload.get("show_seconds", True)
    if not isinstance(show_seconds, bool):
        show_seconds = True

    timezone_name = raw_payload.get("timezone_name", DEFAULT_TIMEZONE_NAME)
    if isinstance(timezone_name, str):
        try:
            timezone_name = _validate_timezone_name(timezone_name)
        except ValueError:
            timezone_name = DEFAULT_TIMEZONE_NAME
    else:
        timezone_name = DEFAULT_TIMEZONE_NAME

    alarms: list[AlarmConfig] = []
    raw_alarms = raw_payload.get("alarms", [])
    if isinstance(raw_alarms, list):
        for raw_alarm in raw_alarms:
            loaded_alarm = _load_alarm(raw_alarm)
            if loaded_alarm is not None:
                alarms.append(loaded_alarm)

    return ClockSettings(
        time_format=time_format,
        show_date=show_date,
        date_format=date_format,
        display_mode=display_mode,
        show_seconds=show_seconds,
        timezone_name=timezone_name,
        alarms=alarms,
    )


def save_settings(settings: ClockSettings) -> None:
    """Persist the current settings, ignoring filesystem errors."""

    settings_path = get_settings_path()
    payload = {
        "time_format": settings.time_format,
        "show_date": settings.show_date,
        "date_format": settings.date_format,
        "display_mode": settings.display_mode,
        "show_seconds": settings.show_seconds,
        "timezone_name": settings.timezone_name,
        "alarms": [
            {
                "hour": alarm.hour,
                "minute": alarm.minute,
                "label": alarm.label,
                "repeat_mode": alarm.repeat_mode,
                "enabled": alarm.enabled,
            }
            for alarm in settings.alarms
        ],
    }

    try:
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings_path.write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )
    except OSError:
        return
