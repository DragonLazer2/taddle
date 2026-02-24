from __future__ import annotations

import json
import logging
import os
from logging.handlers import TimedRotatingFileHandler

from .config import TaddleConfig
from .events import SEVERITY_ORDER, Event, Severity

_SEVERITY_TO_LOGLEVEL = {
    Severity.INFO: logging.INFO,
    Severity.WARNING: logging.WARNING,
    Severity.ALERT: logging.WARNING,
    Severity.CRITICAL: logging.CRITICAL,
}


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        if isinstance(record.msg, dict):
            return json.dumps(record.msg)
        return json.dumps({"message": record.getMessage()})


class TaddleLogger:
    def __init__(self, config: TaddleConfig) -> None:
        self._config = config
        self._logger = logging.getLogger("taddle")
        self._logger.setLevel(logging.DEBUG)
        self._logger.propagate = False
        self._logger.handlers.clear()

        os.makedirs(config.log_dir, exist_ok=True)
        log_path = os.path.join(config.log_dir, config.log_filename)

        file_handler = TimedRotatingFileHandler(
            log_path,
            when=config.log_rotation_when,
            interval=config.log_rotation_interval,
            backupCount=config.log_backup_count,
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(_JsonFormatter())
        self._logger.addHandler(file_handler)

        if config.log_to_stdout:
            stream_handler = logging.StreamHandler()
            threshold = Severity(config.stdout_severity_threshold)
            level = _SEVERITY_TO_LOGLEVEL.get(threshold, logging.WARNING)
            stream_handler.setLevel(level)
            stream_handler.setFormatter(_JsonFormatter())
            self._logger.addHandler(stream_handler)

    def log_event(self, event: Event) -> None:
        level = _SEVERITY_TO_LOGLEVEL.get(event.severity, logging.INFO)
        self._logger.log(level, event.to_dict())

    def shutdown(self) -> None:
        for handler in self._logger.handlers[:]:
            handler.close()
            self._logger.removeHandler(handler)
