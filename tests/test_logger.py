import json
import os

from taddle.config import TaddleConfig
from taddle.events import Event, EventType, Severity
from taddle.logger import TaddleLogger


def test_logger_creates_log_file(log_dir):
    config = TaddleConfig(watch_paths=["/tmp"], log_dir=str(log_dir))
    logger = TaddleLogger(config)
    ev = Event(
        event_type=EventType.FILE_CREATED,
        severity=Severity.INFO,
        source_monitor="test",
        path="/tmp/x",
        description="test",
        event_id="t1",
    )
    logger.log_event(ev)
    logger.shutdown()
    log_path = os.path.join(str(log_dir), "taddle.log")
    assert os.path.exists(log_path)
    with open(log_path) as f:
        line = f.readline()
    data = json.loads(line)
    assert data["event_type"] == "FILE_CREATED"


def test_logger_no_propagation(log_dir):
    config = TaddleConfig(watch_paths=["/tmp"], log_dir=str(log_dir))
    logger = TaddleLogger(config)
    assert logger._logger.propagate is False
    logger.shutdown()
