import json

from taddle.events import Event, EventType, Severity


def test_event_creation():
    ev = Event(
        event_type=EventType.FILE_CREATED,
        severity=Severity.INFO,
        source_monitor="filesystem",
        path="/tmp/test.txt",
        description="File created",
        event_id="abc123",
    )
    assert ev.event_type == EventType.FILE_CREATED
    assert ev.severity == Severity.INFO
    assert ev.path == "/tmp/test.txt"
    assert ev.metadata == {}


def test_event_is_frozen():
    ev = Event(
        event_type=EventType.FILE_CREATED,
        severity=Severity.INFO,
        source_monitor="filesystem",
        path="/tmp/test.txt",
        description="File created",
    )
    try:
        ev.path = "/other"  # type: ignore[misc]
        assert False, "Should have raised"
    except AttributeError:
        pass


def test_to_dict():
    ev = Event(
        event_type=EventType.FILE_DELETED,
        severity=Severity.WARNING,
        source_monitor="filesystem",
        path="/tmp/gone.txt",
        description="deleted",
        event_id="x",
    )
    d = ev.to_dict()
    assert d["event_type"] == "FILE_DELETED"
    assert d["severity"] == "WARNING"
    assert d["path"] == "/tmp/gone.txt"


def test_to_json():
    ev = Event(
        event_type=EventType.FILE_MODIFIED,
        severity=Severity.INFO,
        source_monitor="fs",
        path="/a",
        description="mod",
        event_id="y",
    )
    parsed = json.loads(ev.to_json())
    assert parsed["event_type"] == "FILE_MODIFIED"


def test_event_has_timestamp():
    ev = Event(
        event_type=EventType.FILE_CREATED,
        severity=Severity.INFO,
        source_monitor="fs",
        path="/a",
        description="test",
    )
    assert ev.timestamp  # auto-generated, not empty
