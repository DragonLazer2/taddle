from __future__ import annotations

from dataclasses import dataclass, field

from .events import SEVERITY_ORDER, Severity


@dataclass
class TaddleConfig:
    watch_paths: list[str] = field(default_factory=list)
    recursive: bool = True
    log_dir: str = "logs"
    log_filename: str = "taddle.log"
    log_rotation_when: str = "midnight"
    log_rotation_interval: int = 1
    log_backup_count: int = 7
    log_to_stdout: bool = False
    dedup_window_seconds: float = 60.0
    stdout_severity_threshold: str = "WARNING"
    system_name: str = ""

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.watch_paths:
            errors.append("watch_paths must not be empty")
        if self.dedup_window_seconds < 0:
            errors.append("dedup_window_seconds must be non-negative")
        valid_severities = {s.value for s in Severity}
        if self.stdout_severity_threshold not in valid_severities:
            errors.append(
                f"stdout_severity_threshold must be one of {valid_severities}, "
                f"got '{self.stdout_severity_threshold}'"
            )
        if self.log_backup_count < 0:
            errors.append("log_backup_count must be non-negative")
        return errors
