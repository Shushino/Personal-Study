import unittest
from datetime import datetime

from clock_app.core import ClockSettings
from clock_app.gui import ClockGuiState


class ClockGuiStateTests(unittest.TestCase):
    def test_gui_state_updates_to_12_hour_mode(self) -> None:
        state = ClockGuiState()

        rendered = state.set_time_format(12)

        self.assertEqual(state.settings.time_format, 12)
        self.assertIsInstance(rendered, str)

    def test_gui_state_toggles_date_display(self) -> None:
        state = ClockGuiState(ClockSettings(time_format=24, show_date=False))

        state.set_show_date(True)
        rendered = state.get_display_text(datetime(2026, 4, 16, 15, 4, 5))

        self.assertTrue(state.settings.show_date)
        self.assertEqual(rendered, "2026-04-16 15:04:05")

    def test_gui_state_toggle_method_changes_state_without_errors(self) -> None:
        state = ClockGuiState()

        rendered = state.toggle_show_date()

        self.assertTrue(state.settings.show_date)
        self.assertIsInstance(rendered, str)


if __name__ == "__main__":
    unittest.main()
