from pathlib import Path

import pytest

from codex_session_delete import cli, launcher
from codex_session_delete.launcher import build_codex_command


class FakeServer:
    port = 57321


def test_build_codex_command_adds_remote_debugging_port():
    app_dir = Path("C:/Program Files/WindowsApps/OpenAI.Codex_1.0.0.0_x64__abc/app")

    command = build_codex_command(app_dir, 9229)

    assert str(app_dir / "Codex.exe") in command[0] or str(app_dir / "codex.exe") in command[0]
    assert "--remote-debugging-port=9229" in command



def test_build_codex_command_allows_devtools_websocket_origin():
    app_dir = Path("C:/Program Files/WindowsApps/OpenAI.Codex_1.0.0.0_x64__abc/app")

    command = build_codex_command(app_dir, 9229)

    assert "--remote-allow-origins=http://127.0.0.1:9229" in command



def test_build_codex_command_supports_macos_app_bundle(tmp_path):
    app = tmp_path / "Codex.app"
    executable = app / "Contents" / "MacOS" / "Codex"
    executable.parent.mkdir(parents=True)
    executable.write_text("#!/bin/sh\n", encoding="utf-8")

    command = build_codex_command(app, 9229)

    assert command[0] == str(executable)
    assert "--remote-debugging-port=9229" in command
    assert "--remote-allow-origins=http://127.0.0.1:9229" in command


def test_cli_keeps_helper_server_alive_after_injection(monkeypatch):
    waited = []
    monkeypatch.setattr(cli, "launch_and_inject", lambda *args: FakeServer())
    monkeypatch.setattr(cli, "wait_for_shutdown", lambda server: waited.append(server.port))

    exit_code = cli.main([])

    assert exit_code == 0
    assert waited == [57321]


def test_cli_launch_subcommand_keeps_helper_server_alive_after_injection(monkeypatch):
    waited = []
    calls = []
    monkeypatch.setattr(cli, "launch_and_inject", lambda *args: calls.append(args) or FakeServer())
    monkeypatch.setattr(cli, "wait_for_shutdown", lambda server: waited.append(server.port))

    exit_code = cli.main(["launch"])

    assert exit_code == 0
    assert waited == [57321]
    assert len(calls) == 1


def test_cli_install_dispatches_to_platform_installer(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(cli, "install_codex_plus_plus", lambda options: calls.append(options))

    exit_code = cli.main(["install", "--install-root", str(tmp_path), "--launcher-command", "python -m codex_session_delete"])

    assert exit_code == 0
    assert len(calls) == 1
    assert calls[0].install_root == tmp_path
    assert calls[0].launcher_command == "python -m codex_session_delete"




def test_cli_uninstall_dispatches_to_platform_installer(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(cli, "uninstall_codex_plus_plus", lambda options: calls.append(options))

    exit_code = cli.main(["uninstall", "--install-root", str(tmp_path), "--remove-data"])

    assert exit_code == 0
    assert len(calls) == 1
    assert calls[0].install_root == tmp_path
    assert calls[0].remove_data is True


def test_launch_retries_injection_until_codex_page_is_ready(monkeypatch, tmp_path):
    attempts = []
    monkeypatch.setattr(launcher, "resolve_codex_app_dir", lambda app_dir=None: tmp_path)
    monkeypatch.setattr(launcher, "start_helper", lambda *args, **kwargs: FakeServer())
    monkeypatch.setattr(launcher.subprocess, "Popen", lambda *args, **kwargs: None)

    def inject_after_retry(*args):
        attempts.append(args)
        if len(attempts) == 1:
            raise RuntimeError("CDP page not ready")
        return {"result": {}}

    monkeypatch.setattr(launcher, "inject_file", inject_after_retry)
    monkeypatch.setattr(launcher.time, "sleep", lambda seconds: None)

    server = launcher.launch_and_inject(None, None, tmp_path / "backups", 9229, 57321)

    assert server.port == 57321
    assert len(attempts) == 2


def test_launch_uses_resolved_app_dir(monkeypatch, tmp_path):
    launched = []
    mac_app = tmp_path / "Applications" / "OpenAI Codex.app"
    executable = mac_app / "Contents" / "MacOS" / "Codex"
    executable.parent.mkdir(parents=True)
    executable.write_text("#!/bin/sh\n", encoding="utf-8")
    monkeypatch.setattr(launcher, "resolve_codex_app_dir", lambda app_dir=None: mac_app)
    monkeypatch.setattr(launcher, "start_helper", lambda *args, **kwargs: FakeServer())
    monkeypatch.setattr(launcher.subprocess, "Popen", lambda command: launched.append(command))
    monkeypatch.setattr(launcher, "inject_with_retry", lambda *args, **kwargs: {"result": {}})

    launcher.launch_and_inject(None, None, tmp_path / "backups", 9229, 57321)

    assert launched[0][0] == str(executable)


def test_cli_setup_alias_installs_with_default_launcher(monkeypatch):
    calls = []
    monkeypatch.setattr(cli, "install_codex_plus_plus", lambda options: calls.append(options))

    exit_code = cli.main(["setup"])

    assert exit_code == 0
    assert len(calls) == 1
    assert calls[0].install_root is None
    assert calls[0].launcher_command is None


def test_cli_remove_alias_uninstalls_with_default_options(monkeypatch):
    calls = []
    monkeypatch.setattr(cli, "uninstall_codex_plus_plus", lambda options: calls.append(options))

    exit_code = cli.main(["remove"])

    assert exit_code == 0
    assert len(calls) == 1
    assert calls[0].install_root is None
    assert calls[0].remove_data is False


def test_cli_logs_launch_failure_for_hidden_pythonw(monkeypatch, tmp_path):
    log_path = tmp_path / "codex-plus.log"
    monkeypatch.setattr(cli, "launch_and_inject", lambda *args: (_ for _ in ()).throw(RuntimeError("inject failed")))
    monkeypatch.setattr(cli, "launch_log_path", lambda: log_path)

    with pytest.raises(RuntimeError, match="inject failed"):
        cli.main(["launch"])

    assert "inject failed" in log_path.read_text(encoding="utf-8")
