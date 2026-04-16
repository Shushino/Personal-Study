import unittest
from datetime import datetime

from clock_app.core import (
    ClockController,
    ClockSettings,
    build_display_parts,
    build_display_string,
    format_date,
    format_time,
)


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

    def test_format_date_returns_iso_style_by_default(self) -> None:
        moment = datetime(2026, 4, 16, 15, 7, 9)
        self.assertEqual(format_date(moment), "2026-04-16")

    def test_format_date_supports_day_month_year_slashes(self) -> None:
        moment = datetime(2026, 4, 16, 15, 7, 9)
        self.assertEqual(format_date(moment, "dmy_slash"), "16/04/2026")

    def test_format_date_supports_long_month_style(self) -> None:
        moment = datetime(2026, 4, 16, 15, 7, 9)
        self.assertEqual(format_date(moment, "long_month"), "April 16, 2026")

    def test_format_date_rejects_unknown_styles(self) -> None:
        moment = datetime(2026, 4, 16, 15, 7, 9)

        with self.assertRaises(ValueError):
            format_date(moment, "custom")

    def test_build_display_parts_includes_date_when_enabled(self) -> None:
        moment = datetime(2026, 4, 16, 15, 7, 9)
        settings = ClockSettings(
            time_format=12,
            show_date=True,
            date_format="long_month",
        )
        self.assertEqual(
            build_display_parts(moment, settings),
            ("03:07:09 PM", "April 16, 2026"),
        )

    def test_build_display_string_places_date_below_time(self) -> None:
        moment = datetime(2026, 4, 16, 15, 7, 9)
        settings = ClockSettings(time_format=12, show_date=True)

        self.assertEqual(
            build_display_string(moment, settings),
            "03:07:09 PM\n2026-04-16",
        )


class ClockControllerTests(unittest.TestCase):
    def test_clock_controller_updates_settings(self) -> None:
        controller = ClockController()
        controller.set_time_format(12)
        controller.set_show_date(True)
        controller.set_date_format("dmy_slash")

        rendered = controller.get_display_text(datetime(2026, 4, 16, 21, 8, 10))

        self.assertEqual(controller.settings.time_format, 12)
        self.assertTrue(controller.settings.show_date)
        self.assertEqual(controller.settings.date_format, "dmy_slash")
        self.assertEqual(rendered, "09:08:10 PM\n16/04/2026")


if __name__ == "__main__":
    unittest.main()
