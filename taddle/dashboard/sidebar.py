from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from typing import Any

from . import styles


class Sidebar(tk.Frame):
    """Left panel: system list with colored status dots and badge counts."""

    def __init__(self, parent: tk.Widget, on_select: Callable[[str], None]) -> None:
        super().__init__(parent, bg=styles.BG_SIDEBAR, width=styles.SIDEBAR_WIDTH)
        self.pack_propagate(False)
        self._on_select = on_select
        self._items: dict[str, tk.Frame] = {}
        self._selected: str = "__all__"

        # Title
        title = tk.Label(
            self,
            text="Taddle",
            font=styles.FONT_TITLE,
            fg=styles.ACCENT,
            bg=styles.BG_SIDEBAR,
            anchor=tk.W,
            padx=12,
            pady=8,
        )
        title.pack(fill=tk.X)

        # Separator
        sep = tk.Frame(self, bg=styles.FG_DIM, height=1)
        sep.pack(fill=tk.X, padx=8)

        # Scrollable system list
        self._list_frame = tk.Frame(self, bg=styles.BG_SIDEBAR)
        self._list_frame.pack(fill=tk.BOTH, expand=True, pady=4)

        # Add "All Systems" entry
        self._add_item("__all__", "All Systems", "monitoring", 0)
        self._highlight("__all__")

    def update_systems(self, systems: dict[str, Any], badge_counts: dict[str, int]) -> None:
        known = set(self._items.keys()) - {"__all__"}
        current = set(systems.keys())

        # Add new systems
        for name in current - known:
            info = systems[name]
            self._add_item(name, name, info.get("status", "detached"), badge_counts.get(name, 0))

        # Update existing systems
        for name in current & known:
            info = systems[name]
            self._update_item(name, info.get("status", "detached"), badge_counts.get(name, 0))

        # Remove gone systems
        for name in known - current:
            self._remove_item(name)

        # Update All Systems badge
        total_badge = sum(badge_counts.values())
        self._update_item("__all__", "monitoring", total_badge)

    def _add_item(self, key: str, display_name: str, status: str, badge: int) -> None:
        frame = tk.Frame(self._list_frame, bg=styles.BG_SIDEBAR, cursor="hand2")
        frame.pack(fill=tk.X, padx=4, pady=1)

        dot_color = styles.STATUS_COLORS.get(status, styles.FG_DIM)
        dot = tk.Label(
            frame,
            text="\u25cf",
            fg=dot_color,
            bg=styles.BG_SIDEBAR,
            font=styles.FONT_SMALL,
        )
        dot.pack(side=tk.LEFT, padx=(8, 4))
        dot._status_key = True  # noqa: SLF001 — marker for update

        name_label = tk.Label(
            frame,
            text=display_name,
            fg=styles.FG_PRIMARY,
            bg=styles.BG_SIDEBAR,
            font=styles.FONT_BODY,
            anchor=tk.W,
        )
        name_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        badge_label = tk.Label(
            frame,
            text=f"({badge})" if badge else "",
            fg=styles.FG_DIM,
            bg=styles.BG_SIDEBAR,
            font=styles.FONT_BADGE,
        )
        badge_label.pack(side=tk.RIGHT, padx=(0, 8))

        for widget in (frame, dot, name_label, badge_label):
            widget.bind("<Button-1>", lambda e, k=key: self._on_click(k))

        self._items[key] = frame

    def _update_item(self, key: str, status: str, badge: int) -> None:
        frame = self._items.get(key)
        if not frame:
            return
        children = frame.winfo_children()
        if len(children) >= 1:
            # Update dot color
            dot_color = styles.STATUS_COLORS.get(status, styles.FG_DIM)
            children[0].configure(fg=dot_color)
        if len(children) >= 3:
            # Update badge
            children[2].configure(text=f"({badge})" if badge else "")

    def _remove_item(self, key: str) -> None:
        frame = self._items.pop(key, None)
        if frame:
            frame.destroy()

    def _on_click(self, key: str) -> None:
        self._highlight(key)
        self._selected = key
        self._on_select(key)

    def _highlight(self, key: str) -> None:
        for k, frame in self._items.items():
            bg = styles.BG_CARD if k == key else styles.BG_SIDEBAR
            frame.configure(bg=bg)
            for child in frame.winfo_children():
                child.configure(bg=bg)
        self._selected = key
