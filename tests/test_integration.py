import json
import os
import time

from taddle import Event, Severity, Taddle, TaddleConfig


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
