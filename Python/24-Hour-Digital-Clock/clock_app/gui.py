"""Tkinter GUI front end for the live clock application."""

from __future__ import annotations

import math
import tkinter as tk
from datetime import datetime
from tkinter import ttk

from .core import (
    COMMON_TIMEZONE_NAMES,
    AlarmConfig,
    AlarmEvent,
    AnalogueClockData,
    ClockController,
    ClockSettings,
    format_alarm_summary,
    format_time,
)
from .storage import load_settings, save_settings

DISPLAY_BG = "#111827"
DISPLAY_TEXT = "#E5E7EB"
TIME_TEXT = "#93C5FD"
DATE_TEXT = "#FDE68A"
PANEL_BG = "#F3F4F6"
PANEL_BORDER = "#D1D5DB"
PANEL_TEXT = "#111827"
ERROR_TEXT = "#B91C1C"
SUCCESS_TEXT = "#047857"


class AlarmEditorDialog:
    """Simple modal dialog used to add or edit alarms."""

    def __init__(
        self,
        parent: tk.Tk,
        *,
        title: str,
        alarm: AlarmConfig | None = None,
    ) -> None:
        self.parent = parent
        self.result: AlarmConfig | None = None
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.configure(bg=PANEL_BG)
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.protocol("WM_DELETE_WINDOW", self._on_cancel)

        initial_alarm = alarm or AlarmConfig(hour=7, minute=0)
        repeat_label = "Daily" if initial_alarm.repeat_mode == "daily" else "Once"

        self.time_var = tk.StringVar(
            value=f"{initial_alarm.hour:02d}:{initial_alarm.minute:02d}"
        )
        self.label_var = tk.StringVar(value=initial_alarm.label)
        self.repeat_mode_var = tk.StringVar(value=repeat_label)
        self.enabled_var = tk.BooleanVar(value=initial_alarm.enabled)
        self.error_var = tk.StringVar(value="")

        self._build_widgets()
        self.window.bind("<Return>", self._handle_return_key)
        self.window.bind("<Escape>", self._handle_escape_key)
        self.window.grab_set()
        self.window.focus_force()

    def _build_widgets(self) -> None:
        frame = tk.Frame(self.window, bg=PANEL_BG, padx=16, pady=16)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_columnconfigure(1, weight=1)

        tk.Label(
            frame,
            text="Time (HH:MM)",
            bg=PANEL_BG,
            fg=PANEL_TEXT,
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))
        time_entry = tk.Entry(frame, textvariable=self.time_var, width=18)
        time_entry.grid(row=0, column=1, sticky="ew", pady=(0, 10), padx=(12, 0))

        tk.Label(
            frame,
            text="Label",
            bg=PANEL_BG,
            fg=PANEL_TEXT,
            font=("Segoe UI", 10, "bold"),
        ).grid(row=1, column=0, sticky="w", pady=(0, 10))
        tk.Entry(frame, textvariable=self.label_var).grid(
            row=1,
            column=1,
            sticky="ew",
            pady=(0, 10),
            padx=(12, 0),
        )

        tk.Label(
            frame,
            text="Repeat",
            bg=PANEL_BG,
            fg=PANEL_TEXT,
            font=("Segoe UI", 10, "bold"),
        ).grid(row=2, column=0, sticky="w", pady=(0, 10))
        ttk.Combobox(
            frame,
            textvariable=self.repeat_mode_var,
            values=("Daily", "Once"),
            state="readonly",
            width=16,
        ).grid(row=2, column=1, sticky="ew", pady=(0, 10), padx=(12, 0))

        tk.Checkbutton(
            frame,
            text="Enabled",
            variable=self.enabled_var,
            bg=PANEL_BG,
            fg=PANEL_TEXT,
            activebackground=PANEL_BG,
            selectcolor=PANEL_BG,
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 10))

        tk.Label(
            frame,
            textvariable=self.error_var,
            bg=PANEL_BG,
            fg=ERROR_TEXT,
            wraplength=280,
            justify="left",
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(0, 10))

        buttons = tk.Frame(frame, bg=PANEL_BG)
        buttons.grid(row=5, column=0, columnspan=2, sticky="e")

        tk.Button(buttons, text="Cancel", command=self._on_cancel).pack(
            side="left",
            padx=(0, 8),
        )
        tk.Button(buttons, text="Save", command=self._on_confirm).pack(side="left")

        time_entry.focus_set()

    def _handle_return_key(self, _event: tk.Event[tk.Misc]) -> None:
        self._on_confirm()

    def _handle_escape_key(self, _event: tk.Event[tk.Misc]) -> None:
        self._on_cancel()

    def _build_alarm(self) -> AlarmConfig:
        raw_time = self.time_var.get().strip()
        time_parts = raw_time.split(":")
        if len(time_parts) != 2:
            raise ValueError("Enter the time in HH:MM format.")

        try:
            hour = int(time_parts[0])
            minute = int(time_parts[1])
        except ValueError as exc:
            raise ValueError("Alarm time must use numbers like 07:30.") from exc

        repeat_mode = "daily" if self.repeat_mode_var.get() == "Daily" else "once"
        return AlarmConfig(
            hour=hour,
            minute=minute,
            label=self.label_var.get(),
            repeat_mode=repeat_mode,
            enabled=self.enabled_var.get(),
        )

    def _on_confirm(self) -> None:
        try:
            self.result = self._build_alarm()
        except ValueError as exc:
            self.error_var.set(str(exc))
            return

        self.window.destroy()

    def _on_cancel(self) -> None:
        self.result = None
        self.window.destroy()

    def show(self) -> AlarmConfig | None:
        self.parent.wait_window(self.window)
        return self.result


class ClockGuiState:
    """Testable state wrapper used by the Tkinter UI."""

    def __init__(self, settings: ClockSettings | None = None) -> None:
        self.controller = ClockController(settings)

    @property
    def settings(self) -> ClockSettings:
        return self.controller.settings

    def set_time_format(self, time_format: int) -> tuple[str, str]:
        self.controller.set_time_format(time_format)
        return self.get_display_parts()

    def set_show_date(self, show_date: bool) -> tuple[str, str]:
        self.controller.set_show_date(show_date)
        return self.get_display_parts()

    def set_date_format(self, date_format: str) -> tuple[str, str]:
        self.controller.set_date_format(date_format)
        return self.get_display_parts()

    def set_display_mode(self, display_mode: str) -> tuple[str, str]:
        self.controller.set_display_mode(display_mode)
        return self.get_display_parts()

    def set_show_seconds(self, show_seconds: bool) -> tuple[str, str]:
        self.controller.set_show_seconds(show_seconds)
        return self.get_display_parts()

    def set_timezone_name(self, timezone_name: str) -> tuple[str, str]:
        self.controller.set_timezone_name(timezone_name)
        return self.get_display_parts()

    def toggle_show_date(self) -> tuple[str, str]:
        self.controller.toggle_show_date()
        return self.get_display_parts()

    def add_alarm(self, alarm: AlarmConfig) -> None:
        self.controller.add_alarm(alarm)

    def update_alarm(self, index: int, alarm: AlarmConfig) -> None:
        self.controller.update_alarm(index, alarm)

    def delete_alarm(self, index: int) -> None:
        self.controller.delete_alarm(index)

    def toggle_alarm_enabled(self, index: int) -> bool:
        return self.controller.toggle_alarm_enabled(index)

    def get_alarms(self) -> list[AlarmConfig]:
        return list(self.settings.alarms)

    def get_display_datetime(self, current_time: datetime | None = None) -> datetime:
        return self.controller.get_display_datetime(current_time)

    def get_display_parts(
        self,
        current_time: datetime | None = None,
    ) -> tuple[str, str]:
        return self.controller.get_display_parts(current_time)

    def get_display_text(self, current_time: datetime | None = None) -> str:
        return self.controller.get_display_text(current_time)

    def get_analogue_clock_data(
        self,
        current_time: datetime | None = None,
    ) -> AnalogueClockData:
        return self.controller.get_analogue_clock_data(current_time)

    def check_alarms(self, current_time: datetime | None = None) -> list[AlarmEvent]:
        return self.controller.check_alarms(current_time)


class ClockGuiApp:
    """Desktop clock application."""

    def __init__(self, root: tk.Tk, settings: ClockSettings | None = None) -> None:
        self.root = root
        self.state = ClockGuiState(settings or load_settings())
        self.time_format_var = tk.IntVar(value=self.state.settings.time_format)
        self.show_date_var = tk.BooleanVar(value=self.state.settings.show_date)
        self.date_format_var = tk.StringVar(value=self.state.settings.date_format)
        self.display_mode_var = tk.StringVar(value=self.state.settings.display_mode)
        self.show_seconds_var = tk.BooleanVar(value=self.state.settings.show_seconds)
        self.timezone_var = tk.StringVar(value=self.state.settings.timezone_name)
        self.timezone_feedback_var = tk.StringVar(value="")
        self.alarm_status_var = tk.StringVar(value="Use the buttons to manage alarms.")
        self._after_id: str | None = None

        self.root.title("24-Hour Clock")
        self.root.geometry("780x760")
        self.root.minsize(700, 680)
        self.root.configure(bg=DISPLAY_BG)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self._create_menu()
        self._create_widgets()
        self._refresh_alarm_list()
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

        date_format_menu = tk.Menu(format_menu, tearoff=0)
        date_format_menu.add_radiobutton(
            label="YYYY-MM-DD",
            value="iso",
            variable=self.date_format_var,
            command=self.apply_selected_date_format,
        )
        date_format_menu.add_radiobutton(
            label="DD/MM/YYYY",
            value="dmy_slash",
            variable=self.date_format_var,
            command=self.apply_selected_date_format,
        )
        date_format_menu.add_radiobutton(
            label="Month DD, YYYY",
            value="long_month",
            variable=self.date_format_var,
            command=self.apply_selected_date_format,
        )
        format_menu.add_separator()
        format_menu.add_cascade(label="Date Format", menu=date_format_menu)
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
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        container = tk.Frame(self.root, bg=DISPLAY_BG)
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

        display_frame = tk.Frame(container, bg=DISPLAY_BG, padx=24, pady=24)
        display_frame.grid(row=0, column=0, sticky="nsew")
        display_frame.grid_columnconfigure(0, weight=1)

        tk.Label(
            display_frame,
            text="Live Clock",
            font=("Segoe UI", 20, "bold"),
            fg=DISPLAY_TEXT,
            bg=DISPLAY_BG,
        ).grid(row=0, column=0, pady=(8, 18), sticky="n")

        clock_surface = tk.Frame(display_frame, bg=DISPLAY_BG, height=320)
        clock_surface.grid(row=1, column=0, sticky="nsew")
        clock_surface.grid_columnconfigure(0, weight=1)
        clock_surface.grid_rowconfigure(0, weight=1)

        self.clock_label = tk.Label(
            clock_surface,
            text="",
            font=("Consolas", 32, "bold"),
            fg=TIME_TEXT,
            bg=DISPLAY_BG,
            justify="center",
        )
        self.clock_label.grid(row=0, column=0, sticky="n")

        self.analogue_canvas = tk.Canvas(
            clock_surface,
            width=320,
            height=320,
            bg=DISPLAY_BG,
            highlightthickness=0,
            bd=0,
        )
        self.analogue_canvas.grid(row=0, column=0, sticky="n")

        self.date_label = tk.Label(
            display_frame,
            text="",
            font=("Segoe UI", 16, "bold"),
            fg=DATE_TEXT,
            bg=DISPLAY_BG,
        )
        self.date_label.grid(row=2, column=0, pady=(10, 14), sticky="n")

        tk.Label(
            display_frame,
            text=(
                "Use the menu for time/date formatting and the settings panel "
                "below for display mode, timezone, seconds, and alarms."
            ),
            font=("Segoe UI", 10),
            fg="#9CA3AF",
            bg=DISPLAY_BG,
            wraplength=620,
            justify="center",
        ).grid(row=3, column=0, sticky="n")

        settings_panel = tk.Frame(
            container,
            bg=PANEL_BG,
            padx=18,
            pady=18,
            highlightbackground=PANEL_BORDER,
            highlightthickness=1,
        )
        settings_panel.grid(row=1, column=0, sticky="ew")
        settings_panel.grid_columnconfigure(0, weight=1)
        settings_panel.grid_columnconfigure(1, weight=2)

        display_group = tk.LabelFrame(
            settings_panel,
            text="Display Settings",
            bg=PANEL_BG,
            fg=PANEL_TEXT,
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=12,
        )
        display_group.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        display_group.grid_columnconfigure(1, weight=1)

        tk.Label(
            display_group,
            text="Clock mode",
            bg=PANEL_BG,
            fg=PANEL_TEXT,
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        mode_frame = tk.Frame(display_group, bg=PANEL_BG)
        mode_frame.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 12))
        tk.Radiobutton(
            mode_frame,
            text="Digital",
            value="digital",
            variable=self.display_mode_var,
            command=self.apply_selected_display_mode,
            bg=PANEL_BG,
            fg=PANEL_TEXT,
            activebackground=PANEL_BG,
            selectcolor=PANEL_BG,
        ).pack(side="left", padx=(0, 12))
        tk.Radiobutton(
            mode_frame,
            text="Analogue",
            value="analogue",
            variable=self.display_mode_var,
            command=self.apply_selected_display_mode,
            bg=PANEL_BG,
            fg=PANEL_TEXT,
            activebackground=PANEL_BG,
            selectcolor=PANEL_BG,
        ).pack(side="left")

        tk.Label(
            display_group,
            text="Timezone",
            bg=PANEL_BG,
            fg=PANEL_TEXT,
            font=("Segoe UI", 10, "bold"),
        ).grid(row=2, column=0, sticky="w", pady=(0, 8))

        timezone_row = tk.Frame(display_group, bg=PANEL_BG)
        timezone_row.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        timezone_row.grid_columnconfigure(0, weight=1)

        self.timezone_combo = ttk.Combobox(
            timezone_row,
            textvariable=self.timezone_var,
            values=COMMON_TIMEZONE_NAMES,
        )
        self.timezone_combo.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.timezone_combo.bind(
            "<<ComboboxSelected>>",
            self._handle_timezone_selected,
        )
        self.timezone_combo.bind("<Return>", self._handle_timezone_enter)

        tk.Button(
            timezone_row,
            text="Apply",
            command=self.apply_selected_timezone,
        ).grid(row=0, column=1, sticky="e")

        tk.Label(
            display_group,
            textvariable=self.timezone_feedback_var,
            bg=PANEL_BG,
            fg=ERROR_TEXT,
            wraplength=240,
            justify="left",
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=(0, 8))

        tk.Checkbutton(
            display_group,
            text="Show Seconds",
            variable=self.show_seconds_var,
            command=self.apply_show_seconds_selection,
            bg=PANEL_BG,
            fg=PANEL_TEXT,
            activebackground=PANEL_BG,
            selectcolor=PANEL_BG,
        ).grid(row=5, column=0, columnspan=2, sticky="w")

        alarms_group = tk.LabelFrame(
            settings_panel,
            text="Alarms",
            bg=PANEL_BG,
            fg=PANEL_TEXT,
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=12,
        )
        alarms_group.grid(row=0, column=1, sticky="nsew")
        alarms_group.grid_columnconfigure(0, weight=1)
        alarms_group.grid_rowconfigure(0, weight=1)

        list_container = tk.Frame(alarms_group, bg=PANEL_BG)
        list_container.grid(row=0, column=0, sticky="nsew")
        list_container.grid_columnconfigure(0, weight=1)
        list_container.grid_rowconfigure(0, weight=1)

        self.alarm_listbox = tk.Listbox(list_container, height=8)
        self.alarm_listbox.grid(row=0, column=0, sticky="nsew")
        self.alarm_listbox.bind("<Double-Button-1>", self._handle_alarm_double_click)

        alarm_scrollbar = tk.Scrollbar(
            list_container,
            orient="vertical",
            command=self.alarm_listbox.yview,
        )
        alarm_scrollbar.grid(row=0, column=1, sticky="ns")
        self.alarm_listbox.config(yscrollcommand=alarm_scrollbar.set)

        alarm_buttons = tk.Frame(alarms_group, bg=PANEL_BG)
        alarm_buttons.grid(row=1, column=0, sticky="ew", pady=(10, 8))

        tk.Button(alarm_buttons, text="Add", command=self.add_alarm).pack(
            side="left",
            padx=(0, 8),
        )
        tk.Button(alarm_buttons, text="Edit", command=self.edit_selected_alarm).pack(
            side="left",
            padx=(0, 8),
        )
        tk.Button(
            alarm_buttons,
            text="Delete",
            command=self.delete_selected_alarm,
        ).pack(side="left", padx=(0, 8))
        tk.Button(
            alarm_buttons,
            text="Enable / Disable",
            command=self.toggle_selected_alarm,
        ).pack(side="left")

        tk.Label(
            alarms_group,
            textvariable=self.alarm_status_var,
            bg=PANEL_BG,
            fg=SUCCESS_TEXT,
            wraplength=380,
            justify="left",
        ).grid(row=2, column=0, sticky="w")

    def _handle_timezone_selected(self, _event: tk.Event[tk.Misc]) -> None:
        self.apply_selected_timezone()

    def _handle_timezone_enter(self, _event: tk.Event[tk.Misc]) -> None:
        self.apply_selected_timezone()

    def _handle_alarm_double_click(self, _event: tk.Event[tk.Misc]) -> None:
        self.edit_selected_alarm()

    def _remember_timezone_option(self, timezone_name: str) -> None:
        values = list(self.timezone_combo.cget("values"))
        if timezone_name not in values:
            values.append(timezone_name)
            self.timezone_combo.configure(values=values)

    def _persist_settings(self) -> None:
        save_settings(self.state.settings)

    def _get_selected_alarm_index(self) -> int | None:
        selection = self.alarm_listbox.curselection()
        if not selection:
            self.alarm_status_var.set("Select an alarm first.")
            return None
        return selection[0]

    def _show_alarm_editor(
        self,
        *,
        title: str,
        alarm: AlarmConfig | None = None,
    ) -> AlarmConfig | None:
        dialog = AlarmEditorDialog(self.root, title=title, alarm=alarm)
        return dialog.show()

    def _refresh_alarm_list(self) -> None:
        self.alarm_listbox.delete(0, tk.END)
        for alarm in self.state.get_alarms():
            self.alarm_listbox.insert(tk.END, format_alarm_summary(alarm))

    def _show_alarm_popup(self, event: AlarmEvent) -> None:
        self.root.bell()

        popup = tk.Toplevel(self.root)
        popup.title("Alarm")
        popup.configure(bg=PANEL_BG)
        popup.resizable(False, False)
        popup.transient(self.root)

        time_text = format_time(
            event.triggered_at,
            self.state.settings.time_format,
            False,
            self.state.settings.timezone_name,
        )
        timezone_text = self.state.settings.timezone_name
        label_text = event.alarm.label or "Alarm time reached"

        frame = tk.Frame(popup, bg=PANEL_BG, padx=16, pady=16)
        frame.grid(row=0, column=0, sticky="nsew")

        tk.Label(
            frame,
            text="Alarm",
            bg=PANEL_BG,
            fg=PANEL_TEXT,
            font=("Segoe UI", 14, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        tk.Label(
            frame,
            text=f"{time_text} ({timezone_text})",
            bg=PANEL_BG,
            fg=TIME_TEXT,
            font=("Consolas", 16, "bold"),
        ).grid(row=1, column=0, sticky="w", pady=(0, 8))

        tk.Label(
            frame,
            text=label_text,
            bg=PANEL_BG,
            fg=PANEL_TEXT,
            wraplength=280,
            justify="left",
        ).grid(row=2, column=0, sticky="w", pady=(0, 12))

        tk.Button(frame, text="Dismiss", command=popup.destroy).grid(
            row=3,
            column=0,
            sticky="e",
        )

        popup.lift()
        popup.focus_force()

    def _draw_analogue_clock(self, data: AnalogueClockData) -> None:
        canvas = self.analogue_canvas
        canvas.delete("all")

        width = int(canvas.cget("width"))
        height = int(canvas.cget("height"))
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) * 0.38

        canvas.create_oval(
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
            outline=DISPLAY_TEXT,
            width=3,
        )

        for marker in range(60):
            angle_radians = math.radians((marker * 6) - 90)
            outer_x = center_x + math.cos(angle_radians) * radius
            outer_y = center_y + math.sin(angle_radians) * radius
            inner_radius = radius - (16 if marker % 5 == 0 else 8)
            inner_x = center_x + math.cos(angle_radians) * inner_radius
            inner_y = center_y + math.sin(angle_radians) * inner_radius
            canvas.create_line(
                inner_x,
                inner_y,
                outer_x,
                outer_y,
                fill=DISPLAY_TEXT,
                width=2 if marker % 5 == 0 else 1,
            )

        for hour in range(1, 13):
            angle_radians = math.radians((hour * 30) - 90)
            text_radius = radius - 30
            text_x = center_x + math.cos(angle_radians) * text_radius
            text_y = center_y + math.sin(angle_radians) * text_radius
            canvas.create_text(
                text_x,
                text_y,
                text=str(hour),
                fill=DISPLAY_TEXT,
                font=("Segoe UI", 12, "bold"),
            )

        self._draw_hand(data.hour_angle, radius * 0.5, 6, TIME_TEXT, center_x, center_y)
        self._draw_hand(
            data.minute_angle,
            radius * 0.72,
            4,
            DISPLAY_TEXT,
            center_x,
            center_y,
        )

        if data.second_angle is not None:
            self._draw_hand(
                data.second_angle,
                radius * 0.82,
                2,
                "#F87171",
                center_x,
                center_y,
            )

        canvas.create_oval(
            center_x - 5,
            center_y - 5,
            center_x + 5,
            center_y + 5,
            fill=DATE_TEXT,
            outline="",
        )

    def _draw_hand(
        self,
        angle: float,
        length: float,
        width: int,
        color: str,
        center_x: float,
        center_y: float,
    ) -> None:
        angle_radians = math.radians(angle - 90)
        hand_x = center_x + math.cos(angle_radians) * length
        hand_y = center_y + math.sin(angle_radians) * length
        self.analogue_canvas.create_line(
            center_x,
            center_y,
            hand_x,
            hand_y,
            fill=color,
            width=width,
            capstyle=tk.ROUND,
        )

    def apply_selected_time_format(self) -> None:
        self.state.set_time_format(self.time_format_var.get())
        self._persist_settings()
        self.refresh_display(reschedule=False)

    def apply_selected_date_format(self) -> None:
        self.state.set_date_format(self.date_format_var.get())
        self._persist_settings()
        self.refresh_display(reschedule=False)

    def apply_show_date_selection(self) -> None:
        self.state.set_show_date(self.show_date_var.get())
        self._persist_settings()
        self.refresh_display(reschedule=False)

    def apply_selected_display_mode(self) -> None:
        self.state.set_display_mode(self.display_mode_var.get())
        self._persist_settings()
        self.refresh_display(reschedule=False)

    def apply_show_seconds_selection(self) -> None:
        self.state.set_show_seconds(self.show_seconds_var.get())
        self._persist_settings()
        self.refresh_display(reschedule=False)

    def apply_selected_timezone(self) -> None:
        candidate = self.timezone_var.get().strip()
        try:
            self.state.set_timezone_name(candidate)
        except ValueError:
            self.timezone_feedback_var.set(
                "Enter a valid timezone like UTC or Africa/Lagos."
            )
            self.timezone_var.set(self.state.settings.timezone_name)
            return

        self.timezone_feedback_var.set("")
        self.timezone_var.set(self.state.settings.timezone_name)
        self._remember_timezone_option(self.state.settings.timezone_name)
        self._persist_settings()
        self.refresh_display(reschedule=False)

    def add_alarm(self) -> None:
        alarm = self._show_alarm_editor(title="Add Alarm")
        if alarm is None:
            return
        self.state.add_alarm(alarm)
        self.alarm_status_var.set("Alarm added.")
        self._refresh_alarm_list()
        self._persist_settings()

    def edit_selected_alarm(self) -> None:
        index = self._get_selected_alarm_index()
        if index is None:
            return

        current_alarm = self.state.get_alarms()[index]
        updated_alarm = self._show_alarm_editor(title="Edit Alarm", alarm=current_alarm)
        if updated_alarm is None:
            return

        self.state.update_alarm(index, updated_alarm)
        self.alarm_status_var.set("Alarm updated.")
        self._refresh_alarm_list()
        self.alarm_listbox.selection_set(index)
        self._persist_settings()

    def delete_selected_alarm(self) -> None:
        index = self._get_selected_alarm_index()
        if index is None:
            return

        self.state.delete_alarm(index)
        self.alarm_status_var.set("Alarm deleted.")
        self._refresh_alarm_list()
        self._persist_settings()

    def toggle_selected_alarm(self) -> None:
        index = self._get_selected_alarm_index()
        if index is None:
            return

        enabled = self.state.toggle_alarm_enabled(index)
        self.alarm_status_var.set("Alarm enabled." if enabled else "Alarm disabled.")
        self._refresh_alarm_list()
        self.alarm_listbox.selection_set(index)
        self._persist_settings()

    def refresh_display(self, *, reschedule: bool = True) -> None:
        moment = self.state.get_display_datetime()
        time_text, date_text = self.state.get_display_parts(moment)

        if self.state.settings.display_mode == "digital":
            self.analogue_canvas.grid_remove()
            self.clock_label.grid()
            self.clock_label.config(text=time_text)
        else:
            self.clock_label.grid_remove()
            self.analogue_canvas.grid()
            self._draw_analogue_clock(self.state.get_analogue_clock_data(moment))

        self.date_label.config(text=date_text)
        if date_text:
            self.date_label.grid()
        else:
            self.date_label.grid_remove()

        triggered_alarms = self.state.check_alarms(moment)
        if triggered_alarms:
            self._persist_settings()
            self._refresh_alarm_list()
            for triggered_alarm in triggered_alarms:
                self._show_alarm_popup(triggered_alarm)

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
        self._persist_settings()
        if self.root.winfo_exists():
            self.root.destroy()


def main() -> int:
    """Entrypoint for the GUI launcher."""

    root = tk.Tk()
    ClockGuiApp(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
