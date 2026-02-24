from taddle.config import TaddleConfig


def test_valid_config(watch_dir, log_dir):
    c = TaddleConfig(watch_paths=[str(watch_dir)], log_dir=str(log_dir))
    assert c.validate() == []


def test_empty_watch_paths():
    c = TaddleConfig(watch_paths=[])
    errors = c.validate()
    assert any("watch_paths" in e for e in errors)


def test_invalid_severity_threshold():
    c = TaddleConfig(watch_paths=["/tmp"], stdout_severity_threshold="BOGUS")
    errors = c.validate()
    assert any("stdout_severity_threshold" in e for e in errors)


def test_negative_dedup_window():
    c = TaddleConfig(watch_paths=["/tmp"], dedup_window_seconds=-1)
    errors = c.validate()
    assert any("dedup_window_seconds" in e for e in errors)


def test_negative_backup_count():
    c = TaddleConfig(watch_paths=["/tmp"], log_backup_count=-1)
    errors = c.validate()
    assert any("log_backup_count" in e for e in errors)
