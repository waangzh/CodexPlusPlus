from __future__ import annotations

import plistlib
import shutil
import stat
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from codex_session_delete.installers import InstallOptions


DEFAULT_INSTALL_ROOT = Path("/Applications")
APP_NAME = "Codex++.app"
EXECUTABLE_NAME = "CodexPlusPlus"


def _launcher_command(options: "InstallOptions") -> str:
    if options.launcher_command:
        return options.launcher_command
    return f"{sys.executable} -m codex_session_delete launch"


def _app_root(options: "InstallOptions") -> Path:
    return (options.install_root or DEFAULT_INSTALL_ROOT) / APP_NAME


def install_macos_app(options: "InstallOptions") -> None:
    app = _app_root(options)
    contents = app / "Contents"
    macos = contents / "MacOS"
    resources = contents / "Resources"
    macos.mkdir(parents=True, exist_ok=True)
    resources.mkdir(parents=True, exist_ok=True)

    plist = {
        "CFBundleName": "Codex++",
        "CFBundleDisplayName": "Codex++",
        "CFBundleIdentifier": "com.bigpizzav3.codexplusplus",
        "CFBundleVersion": "0.1.0",
        "CFBundleShortVersionString": "0.1.0",
        "CFBundlePackageType": "APPL",
        "CFBundleExecutable": EXECUTABLE_NAME,
        "LSMinimumSystemVersion": "12.0",
    }
    (contents / "Info.plist").write_bytes(plistlib.dumps(plist))

    executable = macos / EXECUTABLE_NAME
    executable.write_text(f"#!/bin/sh\nexec {_launcher_command(options)}\n", encoding="utf-8")
    executable.chmod(executable.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def uninstall_macos_app(options: "InstallOptions") -> None:
    app = _app_root(options)
    if app.exists():
        shutil.rmtree(app)
