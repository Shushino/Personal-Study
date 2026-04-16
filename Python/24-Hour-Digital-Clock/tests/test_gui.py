import unittest
from datetime import datetime

from clock_app.core import ClockSettings
from clock_app.gui import ClockGuiState


class ClockGuiStateTests(unittest.TestCase):
    def test_gui_state_updates_to_12_hour_mode(self) -> None:
        state = ClockGuiState()

        state.set_time_format(12)
        rendered = state.get_display_parts(datetime(2026, 4, 16, 15, 4, 5))

        self.assertEqual(state.settings.time_format, 12)
        self.assertEqual(rendered, ("03:04:05 PM", ""))

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

    def test_gui_state_toggle_method_preserves_selected_date_format(self) -> None:
        state = ClockGuiState(
            ClockSettings(time_format=12, show_date=True, date_format="dmy_slash")
        )

        state.toggle_show_date()
        state.toggle_show_date()
        rendered = state.get_display_parts(datetime(2026, 4, 16, 15, 4, 5))

        self.assertTrue(state.settings.show_date)
        self.assertEqual(state.settings.date_format, "dmy_slash")
        self.assertEqual(rendered, ("03:04:05 PM", "16/04/2026"))


if __name__ == "__main__":
    unittest.main()
