import pytest

from taddle import TaddleConfig


@pytest.fixture
def watch_dir(tmp_path):
    d = tmp_path / "watched"
    d.mkdir()
    return d


@pytest.fixture
def log_dir(tmp_path):
    d = tmp_path / "logs"
    d.mkdir()
    return d


@pytest.fixture
def sample_config(watch_dir, log_dir):
    return TaddleConfig(
        watch_paths=[str(watch_dir)],
        log_dir=str(log_dir),
        log_to_stdout=False,
    )
