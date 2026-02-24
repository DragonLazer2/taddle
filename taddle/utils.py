from __future__ import annotations

import hashlib
import os
import stat
import time


def compute_event_id(event_type: str, path: str, description: str) -> str:
    payload = f"{event_type}:{path}:{description}"
    return hashlib.sha256(payload.encode()).hexdigest()


def file_hash(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def file_permissions(filepath: str) -> str:
    st = os.stat(filepath)
    return oct(stat.S_IMODE(st.st_mode))


class EventDeduplicator:
    def __init__(self, window_seconds: float = 60.0) -> None:
        self._window = window_seconds
        self._seen: dict[str, float] = {}

    def is_duplicate(self, event_id: str) -> bool:
        now = time.monotonic()
        self._purge(now)
        if event_id in self._seen:
            return True
        self._seen[event_id] = now
        return False

    def _purge(self, now: float) -> None:
        expired = [k for k, t in self._seen.items() if now - t >= self._window]
        for k in expired:
            del self._seen[k]
