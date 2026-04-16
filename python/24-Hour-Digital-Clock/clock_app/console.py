"""Console front end for the live digital clock."""

from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Callable
from datetime import datetime
from typing import TextIO

from .core import ClockController, ClockSettings

HEADER = "=== Live Digital Clock ==="
STOP_MESSAGE = "Clock stopped. Goodbye!"


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser for the console clock."""

    parser = argparse.ArgumentParser(
        description="Run the live digital clock in the terminal."
    )
    parser.add_argument(
        "--format",
        dest="time_format",
        type=int,
        choices=(12, 24),
        default=24,
        help="choose 12-hour or 24-hour time display",
    )
    parser.add_argument(
        "--date",
        dest="show_date",
        action="store_true",
        help="show the current date alongside the time",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> ClockSettings:
    """Parse command-line arguments into clock settings."""

    namespace = build_parser().parse_args(argv)
    return ClockSettings(
        time_format=namespace.time_format,
        show_date=namespace.show_date,
    )


def run_clock(
    settings: ClockSettings,
    *,
    output_stream: TextIO = sys.stdout,
    sleep_func: Callable[[float], None] = time.sleep,
    now_func: Callable[[], datetime] | None = None,
    iterations: int | None = None,
) -> int:
    """Run the live clock loop.

    The optional dependency hooks make the console loop testable without
    changing the user-facing behavior.
    """

    controller = ClockController(settings)
    moment_provider = now_func or datetime.now
    last_display_length = 0
    completed_iterations = 0

    output_stream.write(f"{HEADER}\n")
    output_stream.write("Press Ctrl+C to stop\n\n")
    output_stream.flush()

    try:
        while True:
            display_text = controller.get_display_text(moment_provider())
            padding = " " * max(0, last_display_length - len(display_text))
            output_stream.write(f"\r{display_text}{padding}")
            output_stream.flush()
            last_display_length = len(display_text)
            completed_iterations += 1

            if iterations is not None and completed_iterations >= iterations:
                output_stream.write("\n")
                output_stream.flush()
                return 0

            sleep_func(1)
    except KeyboardInterrupt:
        output_stream.write(f"\n{STOP_MESSAGE}\n")
        output_stream.flush()
        return 0


def main(argv: list[str] | None = None) -> int:
    """Entrypoint for the console launcher."""

    settings = parse_args(argv)
    return run_clock(settings)
