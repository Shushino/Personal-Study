import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from clock_app.core import AlarmConfig, ClockSettings
from clock_app.storage import get_settings_path, load_settings, save_settings


class ClockStorageTests(unittest.TestCase):
    def test_save_and_load_settings_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict("os.environ", {"LOCALAPPDATA": temp_dir}, clear=False):
                settings = ClockSettings(
                    time_format=12,
                    show_date=True,
                    date_format="long_month",
                    display_mode="analogue",
                    show_seconds=False,
                    timezone_name="UTC",
                    alarms=[
                        AlarmConfig(7, 30, "Wake up", "daily"),
                        AlarmConfig(18, 0, "Workout", "once", enabled=False),
                    ],
                )

                save_settings(settings)
                loaded = load_settings()

        self.assertEqual(loaded.time_format, 12)
        self.assertTrue(loaded.show_date)
        self.assertEqual(loaded.date_format, "long_month")
        self.assertEqual(loaded.display_mode, "analogue")
        self.assertFalse(loaded.show_seconds)
        self.assertEqual(loaded.timezone_name, "UTC")
        self.assertEqual(len(loaded.alarms), 2)
        self.assertEqual(loaded.alarms[0].label, "Wake up")
        self.assertEqual(loaded.alarms[1].repeat_mode, "once")
        self.assertFalse(loaded.alarms[1].enabled)

    def test_load_settings_falls_back_to_defaults_for_invalid_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict("os.environ", {"LOCALAPPDATA": temp_dir}, clear=False):
                settings_path = get_settings_path()
                settings_path.parent.mkdir(parents=True, exist_ok=True)
                settings_path.write_text("{not-valid-json}", encoding="utf-8")

                loaded = load_settings()

        self.assertEqual(loaded, ClockSettings())

    def test_load_settings_ignores_invalid_timezone_and_alarm_payloads(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict("os.environ", {"LOCALAPPDATA": temp_dir}, clear=False):
                settings_path = get_settings_path()
                settings_path.parent.mkdir(parents=True, exist_ok=True)
                settings_path.write_text(
                    (
                        '{"time_format": 12, "show_date": true, "date_format": "iso", '
                        '"display_mode": "digital", "show_seconds": true, '
                        '"timezone_name": "Bad/Timezone", "alarms": ['
                        '{"hour": 7, "minute": 30, "label": "Wake up", '
                        '"repeat_mode": "daily", "enabled": true}, '
                        '{"hour": "oops", "minute": 10, "label": 1, '
                        '"repeat_mode": "daily", "enabled": true}'
                        "]}"
                    ),
                    encoding="utf-8",
                )

                loaded = load_settings()

        self.assertEqual(loaded.time_format, 12)
        self.assertEqual(loaded.timezone_name, "Local")
        self.assertEqual(len(loaded.alarms), 1)
        self.assertEqual(loaded.alarms[0].label, "Wake up")

    def test_get_settings_path_uses_local_appdata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict("os.environ", {"LOCALAPPDATA": temp_dir}, clear=False):
                settings_path = get_settings_path()

        self.assertEqual(
            settings_path,
            Path(temp_dir) / "24-Hour-Digital-Clock" / "settings.json",
        )

    def test_get_settings_path_uses_unix_data_directory_when_not_windows(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("clock_app.storage.sys.platform", "linux"), patch(
                "pathlib.Path.home", return_value=Path(temp_dir)
            ):
                settings_path = get_settings_path()

        self.assertEqual(
            settings_path,
            Path(temp_dir)
            / ".local"
            / "share"
            / "24-Hour-Digital-Clock"
            / "settings.json",
        )


if __name__ == "__main__":
    unittest.main()
