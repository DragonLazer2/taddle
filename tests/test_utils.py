import time

from taddle.utils import EventDeduplicator, compute_event_id, file_hash, file_permissions


def test_compute_event_id_deterministic():
    a = compute_event_id("FILE_CREATED", "/tmp/a", "created")
    b = compute_event_id("FILE_CREATED", "/tmp/a", "created")
    assert a == b


def test_compute_event_id_different_inputs():
    a = compute_event_id("FILE_CREATED", "/tmp/a", "created")
    b = compute_event_id("FILE_DELETED", "/tmp/a", "deleted")
    assert a != b


def test_file_hash(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("hello world")
    h = file_hash(str(f))
    assert len(h) == 64  # SHA-256 hex


def test_file_permissions(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("data")
    p = file_permissions(str(f))
    assert p.startswith("0o")


def test_deduplicator_suppresses_duplicates():
    dd = EventDeduplicator(window_seconds=60)
    assert dd.is_duplicate("a") is False
    assert dd.is_duplicate("a") is True
    assert dd.is_duplicate("b") is False


def test_deduplicator_expires(monkeypatch):
    dd = EventDeduplicator(window_seconds=0.1)
    assert dd.is_duplicate("a") is False
    time.sleep(0.15)
    assert dd.is_duplicate("a") is False  # window expired
