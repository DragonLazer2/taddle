from __future__ import annotations

import json
import os
from typing import Any


class LogTailer:
    """Non-blocking JSON-lines file tailer with rotation detection."""

    def __init__(self, log_path: str) -> None:
        self._path = log_path
        self._offset: int = 0
        self._inode: int | None = None

    def read_new_events(self) -> list[dict[str, Any]]:
        if not os.path.exists(self._path):
            return []

        try:
            stat = os.stat(self._path)
        except OSError:
            return []

        current_inode = stat.st_ino

        # Rotation detection: if inode changed, the file was rotated
        if self._inode is not None and current_inode != self._inode:
            self._offset = 0

        self._inode = current_inode

        # If file was truncated (smaller than our offset), reset
        if stat.st_size < self._offset:
            self._offset = 0

        if stat.st_size == self._offset:
            return []

        events: list[dict[str, Any]] = []
        try:
            with open(self._path, "r") as f:
                f.seek(self._offset)
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
                self._offset = f.tell()
        except OSError:
            return []

        return events

    def read_all_events(self) -> list[dict[str, Any]]:
        self._offset = 0
        self._inode = None
        return self.read_new_events()
