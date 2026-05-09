from __future__ import annotations

import socket
import sys
import types
from pathlib import Path

import pytest

from codex_session_delete import watcher


def test_cdp_listening_returns_true_when_bound():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        port = server.getsockname()[1]
        assert watcher.cdp_listening(port) is True


def test_cdp_listening_returns_false_when_closed():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    # After the probe socket closes, nothing should be listening on that port
    # (the port may get reused but the probe finishes with connection refused in normal conditions)
    assert watcher.cdp_listening(port) is False


def test_enable_watcher_removes_flag(tmp_path, monkeypatch):
    monkeypatch.setattr(watcher, "data_root", lambda: tmp_path)
    flag = tmp_path / "watcher.disabled"
    flag.parent.mkdir(parents=True, exist_ok=True)
    flag.touch()
    assert flag.exists()
    watcher.enable_watcher()
    assert not flag.exists()


def test_disable_watcher_creates_flag(tmp_path, monkeypatch):
    monkeypatch.setattr(watcher, "data_root", lambda: tmp_path)
    flag = tmp_path / "watcher.disabled"
    assert not flag.exists()
    watcher.disable_watcher()
    assert flag.exists()


def test_enable_watcher_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.setattr(watcher, "data_root", lambda: tmp_path)
    # Should not raise when flag does not exist
    watcher.enable_watcher()
    assert not (tmp_path / "watcher.disabled").exists()


def test_watch_loop_exits_on_non_windows(monkeypatch, tmp_path):
    monkeypatch.setattr(watcher, "data_root", lambda: tmp_path)
    monkeypatch.setattr(watcher.sys, "platform", "linux")
    assert watcher.watch_loop() == 1


def test_wait_until_no_codex_success(monkeypatch):
    calls = {"n": 0}

    def find() -> list[int]:
        calls["n"] += 1
        # First poll: one process, subsequent polls: empty
        return [1234] if calls["n"] == 1 else []

    monkeypatch.setattr(watcher, "find_codex_processes", find)
    killed: list[list[int]] = []
    monkeypatch.setattr(watcher, "kill_processes", lambda pids: killed.append(list(pids)))
    assert watcher.wait_until_no_codex(timeout=2.0) is True


def test_wait_until_no_codex_times_out(monkeypatch):
    monkeypatch.setattr(watcher, "find_codex_processes", lambda: [1])
    monkeypatch.setattr(watcher, "kill_processes", lambda pids: None)
    assert watcher.wait_until_no_codex(timeout=0.5) is False


def test_wait_for_cdp_returns_true_when_listening(monkeypatch):
    seq = iter([False, False, True])
    monkeypatch.setattr(watcher, "cdp_listening", lambda port: next(seq))
    assert watcher.wait_for_cdp(port=9229, timeout=2.0) is True


def test_wait_for_cdp_returns_false_on_timeout(monkeypatch):
    monkeypatch.setattr(watcher, "cdp_listening", lambda port: False)
    assert watcher.wait_for_cdp(port=9229, timeout=0.3) is False
