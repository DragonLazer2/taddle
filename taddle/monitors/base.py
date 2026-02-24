from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable

from ..config import TaddleConfig
from ..events import Event


class BaseMonitor(ABC):
    def __init__(self, config: TaddleConfig, emit_event: Callable[[Event], None]) -> None:
        self._config = config
        self._emit_event = emit_event

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def start(self) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...

    @abstractmethod
    def scan(self) -> list[Event]: ...
