import unittest
from datetime import datetime

from clock_app.core import AlarmConfig, ClockSettings
from clock_app.gui import ClockGuiState


class ClockGuiStateTests(unittest.TestCase):
    def test_gui_state_updates_to_12_hour_mode(self) -> None:
        state = ClockGuiState()

        state.set_time_format(12)
        rendered = state.get_display_parts(datetime(2026, 4, 16, 15, 4, 5))

        self.assertEqual(state.settings.time_format, 12)
        self.assertEqual(rendered, ("03:04:05 PM", ""))

    def test_gui_state_switches_between_digital_and_analogue_modes(self) -> None:
        state = ClockGuiState()

        state.set_display_mode("analogue")

        self.assertEqual(state.settings.display_mode, "analogue")

    def test_gui_state_toggles_date_display(self) -> None:
        state = ClockGuiState(
            ClockSettings(time_format=24, show_date=False, date_format="iso")
        )

        state.set_show_date(True)
        rendered = state.get_display_parts(datetime(2026, 4, 16, 15, 4, 5))

        self.assertTrue(state.settings.show_date)
        self.assertEqual(rendered, ("15:04:05", "2026-04-16"))

    def test_gui_state_updates_date_format(self) -> None:
        state = ClockGuiState(ClockSettings(show_date=True))

        state.set_date_format("long_month")
        rendered = state.get_display_parts(datetime(2026, 4, 16, 15, 4, 5))

        self.assertEqual(state.settings.date_format, "long_month")
        self.assertEqual(rendered, ("15:04:05", "April 16, 2026"))

    def test_show_seconds_changes_digital_format_and_analogue_second_hand(self) -> None:
        state = ClockGuiState(ClockSettings(display_mode="analogue"))

        state.set_show_seconds(False)
        rendered = state.get_display_parts(datetime(2026, 4, 16, 15, 4, 5))
        analogue_data = state.get_analogue_clock_data(datetime(2026, 4, 16, 15, 4, 5))

        self.assertEqual(rendered, ("15:04", ""))
        self.assertIsNone(analogue_data.second_angle)

    def test_invalid_timezone_preserves_previous_valid_selection(self) -> None:
        state = ClockGuiState(ClockSettings(timezone_name="UTC"))

        with self.assertRaises(ValueError):
            state.set_timezone_name("Bad/Timezone")

        self.assertEqual(state.settings.timezone_name, "UTC")

    def test_alarm_crud_and_toggle_operations_work(self) -> None:
        state = ClockGuiState()
        morning_alarm = AlarmConfig(7, 30, "Wake up", "daily")
        workout_alarm = AlarmConfig(18, 0, "Workout", "once")

        state.add_alarm(morning_alarm)
        state.update_alarm(0, workout_alarm)
        enabled = state.toggle_alarm_enabled(0)
        state.delete_alarm(0)

        self.assertFalse(enabled)
        self.assertEqual(state.get_alarms(), [])

    def test_digital_mode_keeps_time_format_after_switching_back_from_analogue(self) -> None:
        state = ClockGuiState()

        state.set_time_format(12)
        state.set_display_mode("analogue")
        state.set_display_mode("digital")
        rendered = state.get_display_parts(datetime(2026, 4, 16, 15, 4, 5))

        self.assertEqual(state.settings.display_mode, "digital")
        self.assertEqual(rendered, ("03:04:05 PM", ""))


if __name__ == "__main__":
    unittest.main()
