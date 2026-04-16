"""Persistence helpers for the GUI clock settings."""

from __future__ import annotations

import json
import os
from pathlib import Path

from .core import ClockSettings

APP_DIRECTORY_NAME = "24-Hour-Digital-Clock"
SETTINGS_FILE_NAME = "settings.json"


def _default_local_appdata() -> Path:
    return Path.home() / "AppData" / "Local"


def get_settings_path() -> Path:
    """Return the path where GUI settings are stored."""

    base_directory = Path(os.environ.get("LOCALAPPDATA", _default_local_appdata()))
    return base_directory / APP_DIRECTORY_NAME / SETTINGS_FILE_NAME


def load_settings() -> ClockSettings:
    """Load persisted settings and fall back to defaults on any error."""

    settings_path = get_settings_path()
    try:
        raw_payload = json.loads(settings_path.read_text(encoding="utf-8"))
        if not isinstance(raw_payload, dict):
            return ClockSettings()
        show_date = raw_payload.get("show_date", False)
        date_format = raw_payload.get("date_format", "iso")
        if not isinstance(show_date, bool):
            raise ValueError("show_date must be a boolean")
        if not isinstance(date_format, str):
            raise ValueError("date_format must be a string")
        return ClockSettings(
            time_format=int(raw_payload.get("time_format", 24)),
            show_date=show_date,
            date_format=date_format,
        )
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return ClockSettings()


def save_settings(settings: ClockSettings) -> None:
    """Persist the current settings, ignoring filesystem errors."""

    settings_path = get_settings_path()
    payload = {
        "time_format": settings.time_format,
        "show_date": settings.show_date,
        "date_format": settings.date_format,
    }

    try:
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings_path.write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )
    except OSError:
        return
