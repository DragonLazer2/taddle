from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any

from . import styles
from .event_table import EventTable


class OverviewTab(ttk.Frame):
    """All Systems tab: summary cards per system + aggregated event table."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)

        # Header
        header = tk.Frame(self, bg=styles.BG_CONTENT)
        header.pack(fill=tk.X, padx=8, pady=(8, 4))

        tk.Label(
            header,
            text="All Systems Overview",
            font=styles.FONT_HEADING,
            fg=styles.ACCENT,
            bg=styles.BG_CONTENT,
        ).pack(side=tk.LEFT)

        # Cards container
        self._cards_frame = tk.Frame(self, bg=styles.BG_CONTENT)
        self._cards_frame.pack(fill=tk.X, padx=8, pady=4)
        self._cards: dict[str, tk.Frame] = {}

        # Aggregated event table
        self._event_table = EventTable(self, show_system=True)
        self._event_table.pack(fill=tk.BOTH, expand=True, padx=8, pady=(4, 8))

        # Status bar
        self._status_var = tk.StringVar(value="Systems: 0 | Events: 0 | Alerts: 0")
        status_bar = tk.Label(
            self,
            textvariable=self._status_var,
            font=styles.FONT_SMALL,
            fg=styles.FG_SECONDARY,
            bg=styles.BG_CARD,
            anchor=tk.W,
            padx=8,
            pady=4,
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self._total_events = 0
        self._total_alerts = 0

    def update_cards(self, systems: dict[str, Any], badge_counts: dict[str, int]) -> None:
        current = set(systems.keys())
        known = set(self._cards.keys())

        for name in current - known:
            self._add_card(name, systems[name], badge_counts.get(name, 0))

        for name in current & known:
            self._update_card(name, systems[name], badge_counts.get(name, 0))

        for name in known - current:
            card = self._cards.pop(name, None)
            if card:
                card.destroy()

        self._status_var.set(
            f"Systems: {len(systems)} | Events: {self._total_events} | Alerts: {self._total_alerts}"
        )

    def add_event(self, event: dict[str, Any], system_name: str) -> None:
        self._event_table.add_event(event, system_name)
        self._total_events += 1
        if event.get("severity") in ("WARNING", "ALERT", "CRITICAL"):
            self._total_alerts += 1

    def _add_card(self, name: str, info: dict[str, Any], badge: int) -> None:
        card = tk.Frame(self._cards_frame, bg=styles.BG_CARD, padx=12, pady=8)
        card.pack(side=tk.LEFT, padx=4, pady=2)

        status = info.get("status", "detached")
        dot_color = styles.STATUS_COLORS.get(status, styles.FG_DIM)

        header_frame = tk.Frame(card, bg=styles.BG_CARD)
        header_frame.pack(fill=tk.X)

        tk.Label(
            header_frame,
            text="\u25cf",
            fg=dot_color,
            bg=styles.BG_CARD,
            font=styles.FONT_SMALL,
        ).pack(side=tk.LEFT)

        tk.Label(
            header_frame,
            text=name,
            fg=styles.FG_PRIMARY,
            bg=styles.BG_CARD,
            font=styles.FONT_BODY,
        ).pack(side=tk.LEFT, padx=4)

        tk.Label(
            card,
            text=f"Status: {status} | Alerts: {badge}",
            fg=styles.FG_SECONDARY,
            bg=styles.BG_CARD,
            font=styles.FONT_SMALL,
        ).pack(anchor=tk.W)

        self._cards[name] = card

    def _update_card(self, name: str, info: dict[str, Any], badge: int) -> None:
        card = self._cards.get(name)
        if not card:
            return
        # Recreate for simplicity
        card.destroy()
        self._add_card(name, info, badge)
