import json
import os

import pytest

from taddle.dashboard.log_reader import LogTailer


@pytest.fixture
def log_file(tmp_path):
    return tmp_path / "test.log"


def _write_event(log_file, event_type="FILE_CREATED", severity="INFO"):
    event = {
        "event_type": event_type,
        "severity": severity,
        "source_monitor": "filesystem",
        "path": "/tmp/test.txt",
        "description": f"Test event: {event_type}",
        "timestamp": "2026-02-23T10:00:00+00:00",
    }
    with open(log_file, "a") as f:
        f.write(json.dumps(event) + "\n")
    return event


def test_read_all_events(log_file):
    _write_event(log_file, "FILE_CREATED")
    _write_event(log_file, "FILE_MODIFIED")
    _write_event(log_file, "FILE_DELETED", "WARNING")

    tailer = LogTailer(str(log_file))
    events = tailer.read_all_events()
    assert len(events) == 3
    assert events[0]["event_type"] == "FILE_CREATED"
    assert events[1]["event_type"] == "FILE_MODIFIED"
    assert events[2]["event_type"] == "FILE_DELETED"
    assert events[2]["severity"] == "WARNING"


def test_incremental_reads(log_file):
    _write_event(log_file, "FILE_CREATED")

    tailer = LogTailer(str(log_file))
    events1 = tailer.read_new_events()
    assert len(events1) == 1

    # No new events
    events2 = tailer.read_new_events()
    assert len(events2) == 0

    # Add another event
    _write_event(log_file, "FILE_MODIFIED")
    events3 = tailer.read_new_events()
    assert len(events3) == 1
    assert events3[0]["event_type"] == "FILE_MODIFIED"


def test_rotation_detection(log_file):
    """When the file is replaced (rotated), the tailer should read the new file from the start."""
    _write_event(log_file, "FILE_CREATED")

    tailer = LogTailer(str(log_file))
    events1 = tailer.read_new_events()
    assert len(events1) == 1

    # Simulate rotation: remove old file, create new one
    os.remove(str(log_file))
    _write_event(log_file, "FILE_DELETED", "WARNING")

    events2 = tailer.read_new_events()
    assert len(events2) == 1
    assert events2[0]["event_type"] == "FILE_DELETED"


def test_missing_file():
    tailer = LogTailer("/nonexistent/path/to/file.log")
    events = tailer.read_new_events()
    assert events == []


def test_bad_json_lines(log_file):
    """Bad JSON lines should be skipped, valid ones still parsed."""
    with open(log_file, "w") as f:
        f.write('{"event_type": "FILE_CREATED", "severity": "INFO"}\n')
        f.write("NOT VALID JSON\n")
        f.write('{"event_type": "FILE_DELETED", "severity": "WARNING"}\n')

    tailer = LogTailer(str(log_file))
    events = tailer.read_all_events()
    assert len(events) == 2
    assert events[0]["event_type"] == "FILE_CREATED"
    assert events[1]["event_type"] == "FILE_DELETED"


def test_empty_file(log_file):
    log_file.write_text("")
    tailer = LogTailer(str(log_file))
    events = tailer.read_new_events()
    assert events == []


def test_truncated_file(log_file):
    """If the file is truncated (smaller than offset), reset and read from start."""
    _write_event(log_file, "FILE_CREATED")
    _write_event(log_file, "FILE_MODIFIED")

    tailer = LogTailer(str(log_file))
    events1 = tailer.read_new_events()
    assert len(events1) == 2

    # Truncate file and write one event
    log_file.write_text("")
    _write_event(log_file, "FILE_DELETED", "WARNING")

    events2 = tailer.read_new_events()
    assert len(events2) == 1
    assert events2[0]["event_type"] == "FILE_DELETED"
