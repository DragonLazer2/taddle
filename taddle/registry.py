from __future__ import annotations

import fcntl
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REGISTRY_DIR = Path.home() / ".taddle"
REGISTRY_FILE = REGISTRY_DIR / "systems.json"


def _ensure_registry_dir() -> None:
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)


def _read_registry() -> dict[str, Any]:
    if not REGISTRY_FILE.exists():
        return {}
    try:
        text = REGISTRY_FILE.read_text()
        data = json.loads(text)
        if isinstance(data, dict):
            return data
        return {}
    except (json.JSONDecodeError, OSError):
        return {}


def _write_registry(data: dict[str, Any]) -> None:
    _ensure_registry_dir()
    tmp_path = REGISTRY_FILE.with_suffix(".tmp")
    tmp_path.write_text(json.dumps(data, indent=2))
    tmp_path.replace(REGISTRY_FILE)


def _with_lock(func):
    """Decorator that wraps registry operations with file locking."""

    def wrapper(*args, **kwargs):
        _ensure_registry_dir()
        lock_path = REGISTRY_DIR / "registry.lock"
        with open(lock_path, "w") as lock_fd:
            fcntl.flock(lock_fd, fcntl.LOCK_EX)
            try:
                return func(*args, **kwargs)
            finally:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)

    return wrapper


@_with_lock
def register_system(
    system_name: str,
    log_dir: str,
    log_filename: str,
    watch_paths: list[str],
) -> None:
    registry = _read_registry()
    registry[system_name] = {
        "status": "attached",
        "log_dir": log_dir,
        "log_filename": log_filename,
        "watch_paths": watch_paths,
        "registered_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _write_registry(registry)


@_with_lock
def update_system_status(system_name: str, status: str) -> None:
    registry = _read_registry()
    if system_name in registry:
        registry[system_name]["status"] = status
        registry[system_name]["updated_at"] = datetime.now(timezone.utc).isoformat()
        _write_registry(registry)


@_with_lock
def unregister_system(system_name: str) -> None:
    registry = _read_registry()
    if system_name in registry:
        registry[system_name]["status"] = "detached"
        registry[system_name]["updated_at"] = datetime.now(timezone.utc).isoformat()
        _write_registry(registry)


def load_all_systems() -> dict[str, Any]:
    _ensure_registry_dir()
    lock_path = REGISTRY_DIR / "registry.lock"
    with open(lock_path, "w") as lock_fd:
        fcntl.flock(lock_fd, fcntl.LOCK_SH)
        try:
            return _read_registry()
        finally:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
