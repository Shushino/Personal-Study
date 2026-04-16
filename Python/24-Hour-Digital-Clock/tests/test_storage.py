import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from clock_app.core import ClockSettings
from clock_app.storage import get_settings_path, load_settings, save_settings


class ClockStorageTests(unittest.TestCase):
    def test_save_and_load_settings_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict("os.environ", {"LOCALAPPDATA": temp_dir}, clear=False):
                settings = ClockSettings(
                    time_format=12,
                    show_date=True,
                    date_format="long_month",
                )

                save_settings(settings)
                loaded = load_settings()

        self.assertEqual(loaded.time_format, 12)
        self.assertTrue(loaded.show_date)
        self.assertEqual(loaded.date_format, "long_month")

    def test_load_settings_falls_back_to_defaults_for_invalid_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict("os.environ", {"LOCALAPPDATA": temp_dir}, clear=False):
                settings_path = get_settings_path()
                settings_path.parent.mkdir(parents=True, exist_ok=True)
                settings_path.write_text("{not-valid-json}", encoding="utf-8")

                loaded = load_settings()

        self.assertEqual(loaded, ClockSettings())

    def test_load_settings_falls_back_to_defaults_for_invalid_payload_types(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict("os.environ", {"LOCALAPPDATA": temp_dir}, clear=False):
                settings_path = get_settings_path()
                settings_path.parent.mkdir(parents=True, exist_ok=True)
                settings_path.write_text(
                    '{"time_format": "12", "show_date": "yes", "date_format": "iso"}',
                    encoding="utf-8",
                )

                loaded = load_settings()

        self.assertEqual(loaded, ClockSettings())

    def test_get_settings_path_uses_local_appdata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict("os.environ", {"LOCALAPPDATA": temp_dir}, clear=False):
                settings_path = get_settings_path()

        self.assertEqual(
            settings_path,
            Path(temp_dir) / "24-Hour-Digital-Clock" / "settings.json",
        )


if __name__ == "__main__":
    unittest.main()
