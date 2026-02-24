from __future__ import annotations

import os
from collections.abc import Callable

from watchdog.events import (
    FileCreatedEvent,
    FileDeletedEvent,
    FileModifiedEvent,
    FileMovedEvent,
    FileSystemEventHandler,
)
from watchdog.observers import Observer

from ..config import TaddleConfig
from ..events import Event, EventType, Severity
from ..utils import compute_event_id, file_hash, file_permissions
from .base import BaseMonitor


class _TaddleFSHandler(FileSystemEventHandler):
    def __init__(self, emit_event: Callable[[Event], None], monitor_name: str) -> None:
        super().__init__()
        self._emit = emit_event
        self._monitor_name = monitor_name

    def _make_event(self, event_type: EventType, severity: Severity, path: str, description: str) -> Event:
        eid = compute_event_id(event_type.value, path, description)
        return Event(
            event_type=event_type,
            severity=severity,
            source_monitor=self._monitor_name,
            path=path,
            description=description,
            event_id=eid,
        )

    def on_created(self, event: FileCreatedEvent) -> None:
        if event.is_directory:
            return
        ev = self._make_event(EventType.FILE_CREATED, Severity.INFO, event.src_path, f"File created: {event.src_path}")
        self._emit(ev)

    def on_deleted(self, event: FileDeletedEvent) -> None:
        if event.is_directory:
            return
        ev = self._make_event(EventType.FILE_DELETED, Severity.WARNING, event.src_path, f"File deleted: {event.src_path}")
        self._emit(ev)

    def on_modified(self, event: FileModifiedEvent) -> None:
        if event.is_directory:
            return
        ev = self._make_event(EventType.FILE_MODIFIED, Severity.INFO, event.src_path, f"File modified: {event.src_path}")
        self._emit(ev)

    def on_moved(self, event: FileMovedEvent) -> None:
        if event.is_directory:
            return
        ev = self._make_event(
            EventType.FILE_MOVED,
            Severity.WARNING,
            event.src_path,
            f"File moved: {event.src_path} -> {event.dest_path}",
        )
        self._emit(ev)


class FileSystemMonitor(BaseMonitor):
    def __init__(self, config: TaddleConfig, emit_event: Callable[[Event], None]) -> None:
        super().__init__(config, emit_event)
        self._observer: Observer | None = None

    @property
    def name(self) -> str:
        return "filesystem"

    def start(self) -> None:
        handler = _TaddleFSHandler(self._emit_event, self.name)
        self._observer = Observer()
        self._observer.daemon = True
        for path in self._config.watch_paths:
            self._observer.schedule(handler, path, recursive=self._config.recursive)
        self._observer.start()

    def stop(self) -> None:
        if self._observer is not None:
            self._observer.stop()
            self._observer.join(timeout=5)
            self._observer = None

    def scan(self) -> list[Event]:
        events: list[Event] = []
        for watch_path in self._config.watch_paths:
            for root, _dirs, files in os.walk(watch_path):
                for fname in files:
                    fpath = os.path.join(root, fname)
                    try:
                        fh = file_hash(fpath)
                        fp = file_permissions(fpath)
                    except OSError:
                        continue
                    eid = compute_event_id(EventType.SCAN_BASELINE.value, fpath, "baseline")
                    ev = Event(
                        event_type=EventType.SCAN_BASELINE,
                        severity=Severity.INFO,
                        source_monitor=self.name,
                        path=fpath,
                        description=f"Baseline scan: {fpath}",
                        metadata={"hash": fh, "permissions": fp},
                        event_id=eid,
                    )
                    events.append(ev)
        return events
