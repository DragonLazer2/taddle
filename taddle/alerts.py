from __future__ import annotations

import logging
from collections.abc import Callable

from .events import SEVERITY_ORDER, Event, Severity

logger = logging.getLogger("taddle.alerts")


class AlertDispatcher:
    def __init__(self) -> None:
        self._callbacks: list[tuple[Callable[[Event], object], Severity | None]] = []

    def register(self, callback: Callable[[Event], object], severity: Severity | None = None) -> None:
        self._callbacks.append((callback, severity))

    def unregister(self, callback: Callable[[Event], object]) -> None:
        self._callbacks = [(cb, sev) for cb, sev in self._callbacks if cb is not callback]

    def dispatch(self, event: Event) -> None:
        event_order = SEVERITY_ORDER[event.severity]
        for callback, threshold in self._callbacks:
            if threshold is not None and event_order < SEVERITY_ORDER[threshold]:
                continue
            try:
                callback(event)
            except Exception:
                logger.exception("Callback %r raised an exception for event %s", callback, event.event_id)
