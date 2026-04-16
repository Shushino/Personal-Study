import unittest
from datetime import datetime

from clock_app.core import ClockController, ClockSettings, build_display_string, format_date, format_time


class FormatTimeTests(unittest.TestCase):
    def test_format_time_uses_leading_zeros_in_24_hour_mode(self) -> None:
        moment = datetime(2026, 4, 16, 5, 7, 9)
        self.assertEqual(format_time(moment, 24), "05:07:09")

    def test_format_time_handles_midnight_in_12_hour_mode(self) -> None:
        moment = datetime(2026, 4, 16, 0, 5, 9)
        self.assertEqual(format_time(moment, 12), "12:05:09 AM")

    def test_format_time_handles_noon_in_12_hour_mode(self) -> None:
        moment = datetime(2026, 4, 16, 12, 5, 9)
        self.assertEqual(format_time(moment, 12), "12:05:09 PM")

    def test_format_date_returns_expected_calendar_date(self) -> None:
        moment = datetime(2026, 4, 16, 15, 7, 9)
        self.assertEqual(format_date(moment), "2026-04-16")

    def test_build_display_string_includes_date_when_enabled(self) -> None:
        moment = datetime(2026, 4, 16, 15, 7, 9)
        settings = ClockSettings(time_format=12, show_date=True)
        self.assertEqual(
            build_display_string(moment, settings),
            "2026-04-16 03:07:09 PM",
        )


class ClockControllerTests(unittest.TestCase):
    def test_clock_controller_updates_settings(self) -> None:
        controller = ClockController()
        controller.set_time_format(12)
        controller.set_show_date(True)

        rendered = controller.get_display_text(datetime(2026, 4, 16, 21, 8, 10))

        self.assertEqual(controller.settings.time_format, 12)
        self.assertTrue(controller.settings.show_date)
        self.assertEqual(rendered, "2026-04-16 09:08:10 PM")


if __name__ == "__main__":
    unittest.main()
