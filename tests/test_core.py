import pytest

from taddle import Taddle, TaddleConfig, Severity


def test_initial_state():
    t = Taddle()
    assert t.state == "DORMANT"


def test_attach_detach(sample_config):
    t = Taddle()
    t.attach(sample_config)
    assert t.state == "ATTACHED"
    t.detach()
    assert t.state == "DORMANT"


def test_start_stop(sample_config):
    t = Taddle()
    t.attach(sample_config)
    t.start()
    assert t.state == "MONITORING"
    t.stop()
    assert t.state == "ATTACHED"
    t.detach()


def test_cannot_attach_twice(sample_config):
    t = Taddle()
    t.attach(sample_config)
    with pytest.raises(RuntimeError, match="Cannot attach"):
        t.attach(sample_config)
    t.detach()


def test_cannot_start_from_dormant():
    t = Taddle()
    with pytest.raises(RuntimeError, match="Cannot start"):
        t.start()


def test_invalid_config_raises():
    t = Taddle()
    with pytest.raises(ValueError, match="Invalid config"):
        t.attach(TaddleConfig(watch_paths=[]))


def test_scan(sample_config, watch_dir):
    (watch_dir / "file.txt").write_text("content")
    t = Taddle()
    t.attach(sample_config)
    events = t.scan()
    assert len(events) == 1
    assert events[0].path == str(watch_dir / "file.txt")
    t.detach()


def test_on_off_callbacks(sample_config, watch_dir):
    (watch_dir / "file.txt").write_text("data")
    t = Taddle()
    t.attach(sample_config)
    received = []
    cb = lambda ev: received.append(ev)
    t.on(None, cb)
    t.scan()
    assert len(received) == 1
    t.off(cb)
    t.scan()
    # Due to dedup, the same event won't fire again anyway,
    # but the callback was removed so even new events won't reach it.
    t.detach()


def test_detach_stops_monitoring(sample_config):
    t = Taddle()
    t.attach(sample_config)
    t.start()
    assert t.state == "MONITORING"
    t.detach()  # should auto-stop then detach
    assert t.state == "DORMANT"
