import io
import unittest
from datetime import datetime

from clock_app.console import HEADER, parse_args, run_clock


class ParseArgsTests(unittest.TestCase):
    def test_parse_args_uses_default_settings(self) -> None:
        settings = parse_args([])
        self.assertEqual(settings.time_format, 24)
        self.assertFalse(settings.show_date)

    def test_parse_args_supports_date_and_12_hour_mode(self) -> None:
        settings = parse_args(["--format", "12", "--date"])
        self.assertEqual(settings.time_format, 12)
        self.assertTrue(settings.show_date)


class RunClockTests(unittest.TestCase):
    def test_run_clock_writes_header_and_clock_output(self) -> None:
        output = io.StringIO()
        moments = iter(
            [
                datetime(2026, 4, 16, 15, 4, 5),
                datetime(2026, 4, 16, 15, 4, 6),
            ]
        )

        exit_code = run_clock(
            parse_args(["--date"]),
            output_stream=output,
            sleep_func=lambda _: None,
            now_func=lambda: next(moments),
            iterations=2,
        )

        rendered = output.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn(HEADER, rendered)
        self.assertIn("Press Ctrl+C to stop", rendered)
        self.assertIn("\r2026-04-16 15:04:05", rendered)
        self.assertIn("\r2026-04-16 15:04:06", rendered)


if __name__ == "__main__":
    unittest.main()
