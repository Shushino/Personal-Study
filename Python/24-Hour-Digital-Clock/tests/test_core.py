import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from clock_app.core import (
    AlarmConfig,
    ClockController,
    ClockSettings,
    build_analogue_clock_data,
    build_display_parts,
    build_display_string,
    format_date,
    format_time,
)


class FormatTimeTests(unittest.TestCase):
    def test_format_time_uses_leading_zeros_in_24_hour_mode(self) -> None:
        moment = datetime(2026, 4, 16, 5, 7, 9)
        self.assertEqual(format_time(moment, 24, True), "05:07:09")

    def test_format_time_hides_seconds_when_requested(self) -> None:
        moment = datetime(2026, 4, 16, 5, 7, 9)
        self.assertEqual(format_time(moment, 24, False), "05:07")

    def test_format_time_handles_midnight_in_12_hour_mode(self) -> None:
        moment = datetime(2026, 4, 16, 0, 5, 9)
        self.assertEqual(format_time(moment, 12, True), "12:05:09 AM")

    def test_format_time_hides_seconds_in_12_hour_mode(self) -> None:
        moment = datetime(2026, 4, 16, 15, 7, 9)
        self.assertEqual(format_time(moment, 12, False), "03:07 PM")

    def test_format_time_converts_aware_datetimes_to_selected_timezone(self) -> None:
        moment = datetime(2026, 4, 16, 12, 0, 0, tzinfo=ZoneInfo("UTC"))
        self.assertEqual(
            format_time(moment, 24, True, "Africa/Lagos"),
            "13:00:00",
        )

    def test_format_date_returns_iso_style_by_default(self) -> None:
        moment = datetime(2026, 4, 16, 15, 7, 9)
        self.assertEqual(format_date(moment), "2026-04-16")

    def test_format_date_supports_day_month_year_slashes(self) -> None:
        moment = datetime(2026, 4, 16, 15, 7, 9)
        self.assertEqual(format_date(moment, "dmy_slash"), "16/04/2026")

    def test_format_date_supports_long_month_style(self) -> None:
        moment = datetime(2026, 4, 16, 15, 7, 9)
        self.assertEqual(format_date(moment, "long_month"), "April 16, 2026")

    def test_format_date_can_shift_calendar_day_for_selected_timezone(self) -> None:
        moment = datetime(2026, 4, 16, 1, 30, 0, tzinfo=ZoneInfo("UTC"))
        self.assertEqual(
            format_date(moment, "iso", "America/New_York"),
            "2026-04-15",
        )

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

    def test_build_analogue_clock_data_hides_second_hand_when_disabled(self) -> None:
        moment = datetime(2026, 4, 16, 15, 7, 9)

        analogue_data = build_analogue_clock_data(moment, False)

        self.assertIsNone(analogue_data.second_angle)


class ClockControllerTests(unittest.TestCase):
    def test_clock_controller_updates_settings(self) -> None:
        controller = ClockController()
        controller.set_time_format(12)
        controller.set_show_date(True)
        controller.set_date_format("dmy_slash")
        controller.set_show_seconds(False)
        controller.set_display_mode("analogue")

        rendered = controller.get_display_text(datetime(2026, 4, 16, 21, 8, 10))

        self.assertEqual(controller.settings.time_format, 12)
        self.assertTrue(controller.settings.show_date)
        self.assertEqual(controller.settings.date_format, "dmy_slash")
        self.assertTrue(controller.settings.display_mode, "analogue")
        self.assertEqual(rendered, "09:08 PM\n16/04/2026")

    def test_clock_controller_rejects_invalid_timezone(self) -> None:
        controller = ClockController()

        with self.assertRaises(ValueError):
            controller.set_timezone_name("Mars/Base")

    def test_daily_alarm_fires_only_once_per_minute(self) -> None:
        controller = ClockController(
            ClockSettings(
                timezone_name="UTC",
                alarms=[AlarmConfig(9, 30, "Morning check-in", "daily")],
            )
        )
        first_moment = datetime(2026, 4, 16, 9, 30, 5, tzinfo=ZoneInfo("UTC"))
        second_moment = datetime(2026, 4, 16, 9, 30, 45, tzinfo=ZoneInfo("UTC"))

        first_events = controller.check_alarms(first_moment)
        second_events = controller.check_alarms(second_moment)

        self.assertEqual(len(first_events), 1)
        self.assertEqual(first_events[0].alarm.label, "Morning check-in")
        self.assertEqual(second_events, [])
        self.assertTrue(controller.settings.alarms[0].enabled)

    def test_one_time_alarm_auto_disables_after_firing(self) -> None:
        controller = ClockController(
            ClockSettings(
                timezone_name="UTC",
                alarms=[AlarmConfig(18, 45, "Team call", "once")],
            )
        )
        moment = datetime(2026, 4, 16, 18, 45, 0, tzinfo=ZoneInfo("UTC"))

        events = controller.check_alarms(moment)

        self.assertEqual(len(events), 1)
        self.assertFalse(controller.settings.alarms[0].enabled)


if __name__ == "__main__":
    unittest.main()
