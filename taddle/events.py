from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class Severity(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ALERT = "ALERT"
    CRITICAL = "CRITICAL"


SEVERITY_ORDER = {
    Severity.INFO: 0,
    Severity.WARNING: 1,
    Severity.ALERT: 2,
    Severity.CRITICAL: 3,
}


class EventType(Enum):
    FILE_CREATED = "FILE_CREATED"
    FILE_MODIFIED = "FILE_MODIFIED"
    FILE_DELETED = "FILE_DELETED"
    FILE_MOVED = "FILE_MOVED"
    FILE_PERMISSION_CHANGED = "FILE_PERMISSION_CHANGED"
    SCAN_BASELINE = "SCAN_BASELINE"
    MONITOR_STARTED = "MONITOR_STARTED"
    MONITOR_STOPPED = "MONITOR_STOPPED"


@dataclass(frozen=True)
class Event:
    event_type: EventType
    severity: Severity
    source_monitor: str
    path: str
    description: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)
    event_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["event_type"] = self.event_type.value
        d["severity"] = self.severity.value
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict())
