from __future__ import annotations

from collections.abc import Callable
from enum import Enum

from .alerts import AlertDispatcher
from .config import TaddleConfig
from .events import Event, EventType, Severity
from .logger import TaddleLogger
from .monitors.base import BaseMonitor
from .monitors.filesystem import FileSystemMonitor
from .registry import register_system, unregister_system, update_system_status
from .utils import EventDeduplicator, compute_event_id


class _State(Enum):
    DORMANT = "DORMANT"
    ATTACHED = "ATTACHED"
    MONITORING = "MONITORING"


class Taddle:
    def __init__(self) -> None:
        self._state = _State.DORMANT
        self._config: TaddleConfig | None = None
        self._logger: TaddleLogger | None = None
        self._dispatcher: AlertDispatcher | None = None
        self._deduplicator: EventDeduplicator | None = None
        self._monitors: list[BaseMonitor] = []

    @property
    def state(self) -> str:
        return self._state.value

    def attach(self, config: TaddleConfig) -> None:
        if self._state != _State.DORMANT:
            raise RuntimeError(f"Cannot attach: state is {self._state.value}, expected DORMANT")
        errors = config.validate()
        if errors:
            raise ValueError(f"Invalid config: {'; '.join(errors)}")
        self._config = config
        self._logger = TaddleLogger(config)
        self._dispatcher = AlertDispatcher()
        self._deduplicator = EventDeduplicator(config.dedup_window_seconds)
        self._monitors = [FileSystemMonitor(config, self._emit_event)]
        self._state = _State.ATTACHED
        if self._config.system_name:
            register_system(
                self._config.system_name,
                self._config.log_dir,
                self._config.log_filename,
                self._config.watch_paths,
            )

    def detach(self) -> None:
        if self._state == _State.MONITORING:
            self.stop()
        if self._state != _State.ATTACHED:
            raise RuntimeError(f"Cannot detach: state is {self._state.value}, expected ATTACHED")
        if self._config and self._config.system_name:
            unregister_system(self._config.system_name)
        if self._logger:
            self._logger.shutdown()
        self._monitors.clear()
        self._config = None
        self._logger = None
        self._dispatcher = None
        self._deduplicator = None
        self._state = _State.DORMANT

    def start(self) -> None:
        if self._state != _State.ATTACHED:
            raise RuntimeError(f"Cannot start: state is {self._state.value}, expected ATTACHED")
        for monitor in self._monitors:
            monitor.start()
            ev = Event(
                event_type=EventType.MONITOR_STARTED,
                severity=Severity.INFO,
                source_monitor=monitor.name,
                path="",
                description=f"Monitor '{monitor.name}' started",
                event_id=compute_event_id(EventType.MONITOR_STARTED.value, "", monitor.name),
            )
            self._emit_event(ev)
        self._state = _State.MONITORING
        if self._config and self._config.system_name:
            update_system_status(self._config.system_name, "monitoring")

    def stop(self) -> None:
        if self._state != _State.MONITORING:
            raise RuntimeError(f"Cannot stop: state is {self._state.value}, expected MONITORING")
        for monitor in self._monitors:
            monitor.stop()
            ev = Event(
                event_type=EventType.MONITOR_STOPPED,
                severity=Severity.INFO,
                source_monitor=monitor.name,
                path="",
                description=f"Monitor '{monitor.name}' stopped",
                event_id=compute_event_id(EventType.MONITOR_STOPPED.value, "", monitor.name),
            )
            self._emit_event(ev)
        self._state = _State.ATTACHED
        if self._config and self._config.system_name:
            update_system_status(self._config.system_name, "stopped")

    def scan(self) -> list[Event]:
        if self._state not in (_State.ATTACHED, _State.MONITORING):
            raise RuntimeError(f"Cannot scan: state is {self._state.value}, expected ATTACHED or MONITORING")
        all_events: list[Event] = []
        for monitor in self._monitors:
            events = monitor.scan()
            for ev in events:
                self._emit_event(ev)
                all_events.append(ev)
        return all_events

    def on(self, severity: Severity | None, callback: Callable[[Event], object]) -> None:
        if self._dispatcher is None:
            raise RuntimeError("Cannot register callback: not attached")
        self._dispatcher.register(callback, severity)

    def off(self, callback: Callable[[Event], object]) -> None:
        if self._dispatcher is None:
            raise RuntimeError("Cannot unregister callback: not attached")
        self._dispatcher.unregister(callback)

    def add_monitor(self, monitor_class: type[BaseMonitor]) -> None:
        if self._state == _State.DORMANT:
            raise RuntimeError("Cannot add monitor: not attached")
        if self._config is None:
            raise RuntimeError("Cannot add monitor: no config")
        monitor = monitor_class(self._config, self._emit_event)
        self._monitors.append(monitor)
        if self._state == _State.MONITORING:
            monitor.start()

    def _emit_event(self, event: Event) -> None:
        if self._deduplicator and event.event_id and self._deduplicator.is_duplicate(event.event_id):
            return
        if self._logger:
            self._logger.log_event(event)
        if self._dispatcher:
            self._dispatcher.dispatch(event)
