from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any

from . import styles
from .event_table import EventTable

SEVERITY_OPTIONS = ["ALL", "INFO", "WARNING", "ALERT", "CRITICAL"]

SEVERITY_ORDER = {
    "INFO": 0,
    "WARNING": 1,
    "ALERT": 2,
    "CRITICAL": 3,
}


class SystemTab(ttk.Frame):
    """Per-system tab: header, severity filter, event table, count bar."""

    def __init__(self, parent: tk.Widget, system_name: str, system_info: dict[str, Any]) -> None:
        super().__init__(parent)
        self._system_name = system_name
        self._system_info = system_info
        self._filter_severity = "ALL"
        self._all_events: list[dict[str, Any]] = []
        self._event_count = 0
        self._alert_count = 0

        # Header
        header = tk.Frame(self, bg=styles.BG_CONTENT)
        header.pack(fill=tk.X, padx=8, pady=(8, 4))

        status = system_info.get("status", "detached")
        dot_color = styles.STATUS_COLORS.get(status, styles.FG_DIM)

        tk.Label(
            header,
            text="\u25cf",
            fg=dot_color,
            bg=styles.BG_CONTENT,
            font=styles.FONT_HEADING,
        ).pack(side=tk.LEFT)

        tk.Label(
            header,
            text=system_name,
            font=styles.FONT_HEADING,
            fg=styles.FG_PRIMARY,
            bg=styles.BG_CONTENT,
        ).pack(side=tk.LEFT, padx=4)

        self._status_label = tk.Label(
            header,
            text=f"({status})",
            font=styles.FONT_SMALL,
            fg=styles.FG_SECONDARY,
            bg=styles.BG_CONTENT,
        )
        self._status_label.pack(side=tk.LEFT, padx=4)

        # Filter
        filter_frame = tk.Frame(header, bg=styles.BG_CONTENT)
        filter_frame.pack(side=tk.RIGHT)

        tk.Label(
            filter_frame,
            text="Filter:",
            fg=styles.FG_SECONDARY,
            bg=styles.BG_CONTENT,
            font=styles.FONT_SMALL,
        ).pack(side=tk.LEFT, padx=(0, 4))

        self._filter_var = tk.StringVar(value="ALL")
        filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self._filter_var,
            values=SEVERITY_OPTIONS,
            state="readonly",
            width=10,
        )
        filter_combo.pack(side=tk.LEFT)
        filter_combo.bind("<<ComboboxSelected>>", self._on_filter_change)

        # Event table
        self._event_table = EventTable(self)
        self._event_table.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        # Count bar
        self._count_var = tk.StringVar(value="Events: 0 | Alerts: 0")
        count_bar = tk.Label(
            self,
            textvariable=self._count_var,
            font=styles.FONT_SMALL,
            fg=styles.FG_SECONDARY,
            bg=styles.BG_CARD,
            anchor=tk.W,
            padx=8,
            pady=4,
        )
        count_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def add_event(self, event: dict[str, Any]) -> None:
        self._all_events.append(event)
        self._event_count += 1
        severity = event.get("severity", "INFO")
        if severity in ("WARNING", "ALERT", "CRITICAL"):
            self._alert_count += 1

        if self._passes_filter(event):
            self._event_table.add_event(event)

        self._count_var.set(f"Events: {self._event_count} | Alerts: {self._alert_count}")

    def update_status(self, status: str) -> None:
        dot_color = styles.STATUS_COLORS.get(status, styles.FG_DIM)
        header = self.winfo_children()[0]
        children = header.winfo_children()
        if children:
            children[0].configure(fg=dot_color)
        self._status_label.configure(text=f"({status})")

    def _passes_filter(self, event: dict[str, Any]) -> bool:
        if self._filter_severity == "ALL":
            return True
        event_sev = event.get("severity", "INFO")
        return SEVERITY_ORDER.get(event_sev, 0) >= SEVERITY_ORDER.get(self._filter_severity, 0)

    def _on_filter_change(self, _event: tk.Event) -> None:
        self._filter_severity = self._filter_var.get()
        self._event_table.clear()
        for ev in self._all_events:
            if self._passes_filter(ev):
                self._event_table.add_event(ev)
