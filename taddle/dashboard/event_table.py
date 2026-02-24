from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any

from . import styles


class EventTable(ttk.Frame):
    """Treeview-based event list with severity-colored rows."""

    COLUMNS = ("time", "severity", "type", "path", "description")
    HEADERS = ("Time", "Severity", "Type", "Path", "Description")
    WIDTHS = (80, 80, 60, 200, 300)

    def __init__(self, parent: tk.Widget, show_system: bool = False) -> None:
        super().__init__(parent)
        self._show_system = show_system
        self._row_count = 0

        columns = list(self.COLUMNS)
        headers = list(self.HEADERS)
        widths = list(self.WIDTHS)
        if show_system:
            columns.insert(0, "system")
            headers.insert(0, "System")
            widths.insert(0, 100)

        self._tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        for col, header, width in zip(columns, headers, widths):
            self._tree.heading(col, text=header, anchor=tk.W)
            self._tree.column(col, width=width, minwidth=50)

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)

        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure severity tags
        for severity, color in styles.SEVERITY_ROW_COLORS.items():
            self._tree.tag_configure(severity, foreground=color)

    def add_event(self, event: dict[str, Any], system_name: str = "") -> None:
        timestamp = event.get("timestamp", "")
        if "T" in timestamp:
            timestamp = timestamp.split("T")[1][:8]

        values: list[str] = []
        if self._show_system:
            values.append(system_name)
        values.extend([
            timestamp,
            event.get("severity", ""),
            event.get("event_type", "")[:3],
            event.get("path", ""),
            event.get("description", ""),
        ])

        severity = event.get("severity", "INFO")
        self._tree.insert(
            "", 0,
            values=values,
            tags=(severity,),
        )
        self._row_count += 1

        # Enforce max rows
        if self._row_count > styles.MAX_EVENT_ROWS:
            children = self._tree.get_children()
            if children:
                self._tree.delete(children[-1])
                self._row_count -= 1

    def clear(self) -> None:
        for item in self._tree.get_children():
            self._tree.delete(item)
        self._row_count = 0
