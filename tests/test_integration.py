import json
import os
import time

from taddle import Event, Severity, Taddle, TaddleConfig
from taddle.registry import load_all_systems


def test_full_lifecycle(watch_dir, log_dir):
    """Attach -> scan -> start -> create file -> verify callback & log -> stop -> detach."""
    config = TaddleConfig(
        watch_paths=[str(watch_dir)],
        log_dir=str(log_dir),
        log_to_stdout=False,
        dedup_window_seconds=1.0,
    )

    taddle = Taddle()
    taddle.attach(config)

    # Register callback
    received: list[Event] = []
    taddle.on(None, lambda ev: received.append(ev))

    # Baseline scan on empty dir
    baseline = taddle.scan()
    assert baseline == []

    # Start monitoring
    taddle.start()
    assert taddle.state == "MONITORING"

    # The MONITOR_STARTED event should have fired
    started_events = [e for e in received if e.event_type.value == "MONITOR_STARTED"]
    assert len(started_events) == 1

    # Create a file — watchdog should detect it
    test_file = watch_dir / "new_file.txt"
    test_file.write_text("hello taddle")

    # Give watchdog a moment to pick up the event
    deadline = time.time() + 5
    while time.time() < deadline:
        created = [e for e in received if e.event_type.value == "FILE_CREATED"]
        if created:
            break
        time.sleep(0.1)

    assert len(created) >= 1, f"Expected FILE_CREATED event, got: {[e.event_type.value for e in received]}"

    # Stop and detach
    taddle.stop()
    taddle.detach()

    # Verify log file contains JSON events
    log_path = os.path.join(str(log_dir), "taddle.log")
    assert os.path.exists(log_path)
    with open(log_path) as f:
        lines = [l.strip() for l in f if l.strip()]
    assert len(lines) >= 2  # at least MONITOR_STARTED + FILE_CREATED
    for line in lines:
        data = json.loads(line)  # each line is valid JSON
        assert "event_type" in data


def test_registration_lifecycle(watch_dir, log_dir, tmp_path, monkeypatch):
    """Verify dashboard registry is updated through attach -> start -> stop -> detach."""
    # Redirect registry to temp dir
    test_registry_dir = tmp_path / ".taddle"
    test_registry_dir.mkdir()
    test_registry_file = test_registry_dir / "systems.json"
    monkeypatch.setattr("taddle.registry.REGISTRY_DIR", test_registry_dir)
    monkeypatch.setattr("taddle.registry.REGISTRY_FILE", test_registry_file)
    monkeypatch.setattr("taddle.core.register_system",
                        __import__("taddle.registry", fromlist=["register_system"]).register_system)
    monkeypatch.setattr("taddle.core.update_system_status",
                        __import__("taddle.registry", fromlist=["update_system_status"]).update_system_status)
    monkeypatch.setattr("taddle.core.unregister_system",
                        __import__("taddle.registry", fromlist=["unregister_system"]).unregister_system)

    config = TaddleConfig(
        watch_paths=[str(watch_dir)],
        log_dir=str(log_dir),
        log_to_stdout=False,
        system_name="test-system",
    )

    t = Taddle()

    # Attach — should register with status "attached"
    t.attach(config)
    systems = load_all_systems()
    assert "test-system" in systems
    assert systems["test-system"]["status"] == "attached"
    assert systems["test-system"]["log_dir"] == str(log_dir)

    # Start — status should become "monitoring"
    t.start()
    systems = load_all_systems()
    assert systems["test-system"]["status"] == "monitoring"

    # Stop — status should become "stopped"
    t.stop()
    systems = load_all_systems()
    assert systems["test-system"]["status"] == "stopped"

    # Detach — status should become "detached"
    t.detach()
    systems = load_all_systems()
    assert systems["test-system"]["status"] == "detached"


def test_no_registration_without_system_name(watch_dir, log_dir, tmp_path, monkeypatch):
    """Systems without system_name should not appear in the registry."""
    test_registry_dir = tmp_path / ".taddle"
    test_registry_dir.mkdir()
    test_registry_file = test_registry_dir / "systems.json"
    monkeypatch.setattr("taddle.registry.REGISTRY_DIR", test_registry_dir)
    monkeypatch.setattr("taddle.registry.REGISTRY_FILE", test_registry_file)

    config = TaddleConfig(
        watch_paths=[str(watch_dir)],
        log_dir=str(log_dir),
        log_to_stdout=False,
        # system_name is empty (default)
    )

    t = Taddle()
    t.attach(config)
    t.start()
    t.stop()
    t.detach()

    systems = load_all_systems()
    assert systems == {}
