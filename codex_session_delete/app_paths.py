from __future__ import annotations

import os
import re
from pathlib import Path


_VERSION_RE = re.compile(r"OpenAI\.Codex_([0-9.]+)_")


def _version_tuple(path: Path) -> tuple[int, ...]:
    match = _VERSION_RE.search(path.name)
    if not match:
        return ()
    return tuple(int(part) for part in match.group(1).split(".") if part.isdigit())


def find_latest_codex_app_dir(windows_apps_dir: Path | None = None) -> Path | None:
    root = windows_apps_dir or Path("C:/Program Files/WindowsApps")
    candidates = [path / "app" for path in root.glob("OpenAI.Codex_*_x64__*") if (path / "app").is_dir()]
    if not candidates:
        return None
    return max(candidates, key=lambda app_dir: _version_tuple(app_dir.parent))


def user_data_candidates() -> list[Path]:
    candidates: list[Path] = []
    local = os.environ.get("LOCALAPPDATA")
    roaming = os.environ.get("APPDATA")
    if local:
        candidates.extend([
            Path(local) / "OpenAI" / "Codex",
            Path(local) / "OpenAI.Codex",
            Path(local) / "Codex",
        ])
    if roaming:
        candidates.extend([
            Path(roaming) / "OpenAI" / "Codex",
            Path(roaming) / "OpenAI.Codex",
            Path(roaming) / "Codex",
        ])
    return candidates


def find_macos_codex_app(candidates: list[Path] | None = None) -> Path | None:
    search = candidates or [Path("/Applications/Codex.app"), Path.home() / "Applications" / "Codex.app"]
    for path in search:
        if path.is_dir():
            return path
    return None
