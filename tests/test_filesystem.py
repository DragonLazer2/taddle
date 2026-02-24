import os

from taddle.config import TaddleConfig
from taddle.monitors.filesystem import FileSystemMonitor


def test_scan_finds_files(watch_dir, log_dir):
    (watch_dir / "a.txt").write_text("aaa")
    (watch_dir / "b.txt").write_text("bbb")
    config = TaddleConfig(watch_paths=[str(watch_dir)], log_dir=str(log_dir))
    events_collected = []
    monitor = FileSystemMonitor(config, lambda ev: events_collected.append(ev))
    results = monitor.scan()
    assert len(results) == 2
    paths = {ev.path for ev in results}
    assert str(watch_dir / "a.txt") in paths
    assert str(watch_dir / "b.txt") in paths
    for ev in results:
        assert "hash" in ev.metadata
        assert "permissions" in ev.metadata


def test_scan_empty_dir(watch_dir, log_dir):
    config = TaddleConfig(watch_paths=[str(watch_dir)], log_dir=str(log_dir))
    monitor = FileSystemMonitor(config, lambda ev: None)
    results = monitor.scan()
    assert results == []
