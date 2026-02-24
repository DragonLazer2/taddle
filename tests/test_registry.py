import json
import os
import threading

import pytest

from taddle.registry import (
    REGISTRY_DIR,
    REGISTRY_FILE,
    load_all_systems,
    register_system,
    unregister_system,
    update_system_status,
)


@pytest.fixture(autouse=True)
def clean_registry(tmp_path, monkeypatch):
    """Redirect registry to a temp directory so tests don't pollute ~/.taddle."""
    test_dir = tmp_path / ".taddle"
    test_dir.mkdir()
    test_file = test_dir / "systems.json"
    monkeypatch.setattr("taddle.registry.REGISTRY_DIR", test_dir)
    monkeypatch.setattr("taddle.registry.REGISTRY_FILE", test_file)
    return test_dir, test_file


def test_register_system(clean_registry):
    _dir, reg_file = clean_registry
    register_system("web-server", "/tmp/logs", "taddle.log", ["/var/www"])
    data = json.loads(reg_file.read_text())
    assert "web-server" in data
    assert data["web-server"]["status"] == "attached"
    assert data["web-server"]["log_dir"] == "/tmp/logs"
    assert data["web-server"]["watch_paths"] == ["/var/www"]


def test_update_system_status(clean_registry):
    register_system("web-server", "/tmp/logs", "taddle.log", ["/var/www"])
    update_system_status("web-server", "monitoring")
    data = load_all_systems()
    assert data["web-server"]["status"] == "monitoring"


def test_unregister_system(clean_registry):
    register_system("web-server", "/tmp/logs", "taddle.log", ["/var/www"])
    unregister_system("web-server")
    data = load_all_systems()
    assert data["web-server"]["status"] == "detached"


def test_update_nonexistent_system(clean_registry):
    """Updating a system that doesn't exist is a no-op."""
    update_system_status("ghost", "monitoring")
    data = load_all_systems()
    assert "ghost" not in data


def test_unregister_nonexistent_system(clean_registry):
    """Unregistering a system that doesn't exist is a no-op."""
    unregister_system("ghost")
    data = load_all_systems()
    assert "ghost" not in data


def test_load_empty_registry(clean_registry):
    data = load_all_systems()
    assert data == {}


def test_concurrent_writes(clean_registry):
    """Multiple threads registering systems concurrently should not corrupt the file."""
    barrier = threading.Barrier(5)

    def register(name):
        barrier.wait()
        register_system(name, "/tmp/logs", "taddle.log", ["/tmp"])

    threads = [threading.Thread(target=register, args=(f"system-{i}",)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    data = load_all_systems()
    assert len(data) == 5
    for i in range(5):
        assert f"system-{i}" in data


def test_corrupted_file_recovery(clean_registry):
    """If the registry file contains invalid JSON, operations should recover gracefully."""
    _dir, reg_file = clean_registry
    reg_file.write_text("NOT VALID JSON {{{")
    # Register should overwrite the corrupted file
    register_system("fresh", "/tmp/logs", "taddle.log", ["/tmp"])
    data = load_all_systems()
    assert "fresh" in data
    assert data["fresh"]["status"] == "attached"


def test_multiple_systems(clean_registry):
    register_system("alpha", "/tmp/a", "a.log", ["/a"])
    register_system("beta", "/tmp/b", "b.log", ["/b"])
    register_system("gamma", "/tmp/c", "c.log", ["/c"])

    data = load_all_systems()
    assert len(data) == 3
    assert data["alpha"]["log_dir"] == "/tmp/a"
    assert data["beta"]["log_dir"] == "/tmp/b"
    assert data["gamma"]["log_dir"] == "/tmp/c"
