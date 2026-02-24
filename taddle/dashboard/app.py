from __future__ import annotations

import os
import tkinter as tk
from tkinter import ttk
from typing import Any

from ..registry import load_all_systems
from . import styles
from .log_reader import LogTailer
from .overview_tab import OverviewTab
from .sidebar import Sidebar
from .system_tab import SystemTab


class DashboardApp(tk.Tk):
    """Main dashboard window with polling loops and tab switching."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Taddle Dashboard")
        self.geometry("1000x600")
        self.configure(bg=styles.BG_DARK)
        self.minsize(800, 400)

        self._systems: dict[str, Any] = {}
        self._tailers: dict[str, LogTailer] = {}
        self._system_tabs: dict[str, SystemTab] = {}
        self._badge_counts: dict[str, int] = {}
        self._current_tab: str = "__all__"

        # Configure ttk style
        self._style = ttk.Style(self)
        self._style.theme_use("clam")
        self._configure_styles()

        # Layout: sidebar + content
        self._sidebar = Sidebar(self, on_select=self._on_system_select)
        self._sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self._content = tk.Frame(self, bg=styles.BG_CONTENT)
        self._content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Overview tab (always exists)
        self._overview = OverviewTab(self._content)
        self._overview.pack(fill=tk.BOTH, expand=True)

        # Start polling
        self.after(100, self._poll_registry)
        self.after(500, self._poll_logs)

    def _configure_styles(self) -> None:
        self._style.configure(
            "Treeview",
            background=styles.BG_TABLE_ROW,
            foreground=styles.FG_PRIMARY,
            fieldbackground=styles.BG_TABLE_ROW,
            font=styles.FONT_MONO,
            rowheight=24,
        )
        self._style.configure(
            "Treeview.Heading",
            background=styles.BG_CARD,
            foreground=styles.FG_PRIMARY,
            font=styles.FONT_BODY,
        )
        self._style.map("Treeview", background=[("selected", styles.ACCENT)])
        self._style.configure("TFrame", background=styles.BG_CONTENT)
        self._style.configure("TCombobox", fieldbackground=styles.BG_CARD)

    def _poll_registry(self) -> None:
        try:
            systems = load_all_systems()
        except Exception:
            systems = {}

        new_systems = set(systems.keys()) - set(self._systems.keys())
        gone_systems = set(self._systems.keys()) - set(systems.keys())

        for name in new_systems:
            info = systems[name]
            log_path = os.path.join(info.get("log_dir", ""), info.get("log_filename", ""))
            self._tailers[name] = LogTailer(log_path)
            self._badge_counts[name] = 0
            tab = SystemTab(self._content, name, info)
            self._system_tabs[name] = tab

        for name in gone_systems:
            self._tailers.pop(name, None)
            self._badge_counts.pop(name, None)
            tab = self._system_tabs.pop(name, None)
            if tab:
                tab.destroy()

        # Update status of existing systems
        for name, info in systems.items():
            if name in self._system_tabs:
                self._system_tabs[name].update_status(info.get("status", "detached"))

        self._systems = systems
        self._sidebar.update_systems(systems, self._badge_counts)
        self._overview.update_cards(systems, self._badge_counts)

        self.after(styles.REGISTRY_POLL_MS, self._poll_registry)

    def _poll_logs(self) -> None:
        for name, tailer in self._tailers.items():
            try:
                events = tailer.read_new_events()
            except Exception:
                continue

            for event in events:
                severity = event.get("severity", "INFO")
                if severity in ("WARNING", "ALERT", "CRITICAL"):
                    self._badge_counts[name] = self._badge_counts.get(name, 0) + 1

                # Add to system tab
                tab = self._system_tabs.get(name)
                if tab:
                    tab.add_event(event)

                # Add to overview
                self._overview.add_event(event, name)

        self._sidebar.update_systems(self._systems, self._badge_counts)
        self.after(styles.LOG_POLL_MS, self._poll_logs)

    def _on_system_select(self, key: str) -> None:
        self._current_tab = key

        # Hide all tabs
        self._overview.pack_forget()
        for tab in self._system_tabs.values():
            tab.pack_forget()

        # Show selected
        if key == "__all__":
            self._overview.pack(fill=tk.BOTH, expand=True)
        elif key in self._system_tabs:
            self._system_tabs[key].pack(fill=tk.BOTH, expand=True)
