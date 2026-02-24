# Taddle

Passive security monitoring library for Python. Taddle watches for suspicious file system activity, logs everything with timestamps, and notifies your application through callbacks. It never takes action — it only records, flags, and alerts.

## Features

- **Inert by default** — safe to import, must be explicitly attached to activate
- **File system monitoring** — detects file creation, modification, deletion, and moves via [watchdog](https://github.com/gorakhargosh/watchdog)
- **JSON-lines logging** — each log line is independently parseable, with timed rotation
- **Callback alerts** — register callbacks filtered by severity level
- **Event deduplication** — sliding time window prevents log flooding
- **Plugin architecture** — add custom monitors without changing the core
- **Non-intrusive** — daemon threads never outlive the host, isolated logging never pollutes host logs

## Installation

```bash
pip install -e ".[dev]"
```

## Quick Start

```python
from taddle import Taddle, TaddleConfig, Event, Severity

config = TaddleConfig(
    watch_paths=["/var/app/data", "/etc/myapp"],
    log_dir="/var/log/taddle",
    log_to_stdout=True,
)

taddle = Taddle()
taddle.attach(config)

def on_warning(event: Event):
    print(f"ALERT: {event.description}")

taddle.on(Severity.WARNING, on_warning)
taddle.scan()   # one-time baseline sweep
taddle.start()  # begin background monitoring

# ... host app runs, taddle monitors silently ...

taddle.stop()
taddle.detach()
```

## Configuration

`TaddleConfig` accepts the following fields:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `watch_paths` | `list[str]` | `[]` | Directories to monitor (required) |
| `recursive` | `bool` | `True` | Watch subdirectories |
| `log_dir` | `str` | `"logs"` | Log output directory |
| `log_filename` | `str` | `"taddle.log"` | Log file name |
| `log_rotation_when` | `str` | `"midnight"` | When to rotate logs |
| `log_rotation_interval` | `int` | `1` | Rotation interval |
| `log_backup_count` | `int` | `7` | Number of rotated logs to keep |
| `log_to_stdout` | `bool` | `False` | Also print events to stdout |
| `dedup_window_seconds` | `float` | `60.0` | Suppress duplicate events within this window |
| `stdout_severity_threshold` | `str` | `"WARNING"` | Minimum severity for stdout output |

## Severity Levels

- **INFO** — routine activity (file created, file modified)
- **WARNING** — noteworthy activity (file deleted, file moved)
- **ALERT** — suspicious activity
- **CRITICAL** — requires immediate attention

## Adding Custom Monitors

Subclass `BaseMonitor` and register it:

```python
from taddle.monitors.base import BaseMonitor
from taddle.events import Event

class NetworkMonitor(BaseMonitor):
    @property
    def name(self) -> str:
        return "network"

    def start(self) -> None: ...
    def stop(self) -> None: ...
    def scan(self) -> list[Event]: ...

taddle.add_monitor(NetworkMonitor)
```

## Running Tests

```bash
pytest tests/ -v
```

## License

MIT
