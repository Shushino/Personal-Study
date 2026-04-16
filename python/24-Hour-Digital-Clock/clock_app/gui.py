"""Tkinter GUI front end for the live digital clock."""

from __future__ import annotations

import tkinter as tk
from datetime import datetime

from .core import ClockController, ClockSettings


class ClockGuiState:
    """Testable state wrapper used by the Tkinter UI."""

    def __init__(self, settings: ClockSettings | None = None) -> None:
        self.controller = ClockController(settings)

    @property
    def settings(self) -> ClockSettings:
        return self.controller.settings

    def set_time_format(self, time_format: int) -> str:
        self.controller.set_time_format(time_format)
        return self.get_display_text()

    def set_show_date(self, show_date: bool) -> str:
        self.controller.set_show_date(show_date)
        return self.get_display_text()

    def toggle_show_date(self) -> str:
        self.controller.toggle_show_date()
        return self.get_display_text()

    def get_display_text(self, current_time: datetime | None = None) -> str:
        return self.controller.get_display_text(current_time)


class ClockGuiApp:
    """Desktop clock application."""

    def __init__(self, root: tk.Tk, settings: ClockSettings | None = None) -> None:
        self.root = root
        self.state = ClockGuiState(settings)
        self.time_format_var = tk.IntVar(value=self.state.settings.time_format)
        self.show_date_var = tk.BooleanVar(value=self.state.settings.show_date)
        self._after_id: str | None = None

        self.root.title("Digital Clock")
        self.root.geometry("460x220")
        self.root.minsize(420, 200)
        self.root.configure(bg="#111827")
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self._create_menu()
        self._create_widgets()
        self.refresh_display()

    def _create_menu(self) -> None:
        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.close)
        menu_bar.add_cascade(label="File", menu=file_menu)

        format_menu = tk.Menu(menu_bar, tearoff=0)
        format_menu.add_radiobutton(
            label="12-hour",
            value=12,
            variable=self.time_format_var,
            command=self.apply_selected_time_format,
        )
        format_menu.add_radiobutton(
            label="24-hour",
            value=24,
            variable=self.time_format_var,
            command=self.apply_selected_time_format,
        )
        menu_bar.add_cascade(label="Format", menu=format_menu)

        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_checkbutton(
            label="Show Date",
            variable=self.show_date_var,
            command=self.apply_show_date_selection,
        )
        menu_bar.add_cascade(label="View", menu=view_menu)

        self.root.config(menu=menu_bar)

    def _create_widgets(self) -> None:
        frame = tk.Frame(self.root, bg="#111827", padx=24, pady=24)
        frame.pack(fill="both", expand=True)

        title_label = tk.Label(
            frame,
            text="Live Digital Clock",
            font=("Segoe UI", 18, "bold"),
            fg="#E5E7EB",
            bg="#111827",
        )
        title_label.pack(pady=(12, 18))

        self.clock_label = tk.Label(
            frame,
            text="",
            font=("Consolas", 28, "bold"),
            fg="#93C5FD",
            bg="#111827",
        )
        self.clock_label.pack(pady=(0, 12))

        help_label = tk.Label(
            frame,
            text="Use the menu to switch time format or show the date.",
            font=("Segoe UI", 10),
            fg="#9CA3AF",
            bg="#111827",
        )
        help_label.pack()

    def apply_selected_time_format(self) -> None:
        self.state.set_time_format(self.time_format_var.get())
        self.refresh_display(reschedule=False)

    def apply_show_date_selection(self) -> None:
        self.state.set_show_date(self.show_date_var.get())
        self.refresh_display(reschedule=False)

    def refresh_display(self, *, reschedule: bool = True) -> None:
        self.clock_label.config(text=self.state.get_display_text())
        if reschedule:
            self._schedule_next_refresh()

    def _schedule_next_refresh(self) -> None:
        if self._after_id is not None:
            self.root.after_cancel(self._after_id)
        self._after_id = self.root.after(1000, self._handle_scheduled_refresh)

    def _handle_scheduled_refresh(self) -> None:
        self._after_id = None
        self.refresh_display()

    def close(self) -> None:
        if self._after_id is not None:
            self.root.after_cancel(self._after_id)
            self._after_id = None
        if self.root.winfo_exists():
            self.root.destroy()


def main() -> int:
    """Entrypoint for the GUI launcher."""

    root = tk.Tk()
    ClockGuiApp(root)
    root.mainloop()
    return 0
