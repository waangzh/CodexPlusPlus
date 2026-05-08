import subprocess
from pathlib import Path


def test_renderer_script_exists_and_parses_with_node():
    script = Path("codex_session_delete/inject/renderer-inject.js")
    assert script.exists()
    result = subprocess.run(["node", "--check", str(script)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_renderer_script_contains_hover_delete_contract():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    assert "codex-delete-button" in text
    assert "MutationObserver" in text
    assert "confirmDelete" in text
    assert "/delete" in text
    assert "/undo" in text


def test_renderer_script_supports_codex_sidebar_thread_attributes():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    assert "data-app-action-sidebar-thread-id" in text
    assert "data-thread-title" in text


def test_renderer_script_positions_delete_button_without_affecting_layout():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    assert "position: absolute" in text
    assert "right: 28px" in text
    assert "top: 50%" in text
    assert "transform: translateY(-50%)" in text




def test_renderer_script_enables_plugin_entry_for_api_key_users():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    assert "enablePluginEntry" in text
    assert "disabled = false" in text
    assert "removeAttribute(\"disabled\")" in text
    assert "setAuthMethod(\"chatgpt\")" in text
    assert "__reactFiber" in text
    assert "/skills/plugins" not in text
    assert "skillProps.onClick" not in text


def test_renderer_script_unblocks_connector_unavailable_plugin_install_buttons():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    assert "unblockPluginInstallButtons" in text
    assert "App unavailable" in text
    assert "document.body.textContent" in text
    assert "button.disabled = false" in text
    assert "removeAttribute(\"aria-disabled\")" in text


def test_renderer_script_debounces_mutation_observer_scan():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    assert "scanLightweight" in text
    assert "scanDeferred" in text
    assert "requestAnimationFrame(scanDeferred)" in text
    assert "sessionRows().forEach(attachButton)" in text
    assert "new MutationObserver(scheduleScan)" in text
    assert "new MutationObserver(scan)" not in text
    assert "scheduleScan();" in text
    assert "  scan();\n  window.__codexSessionDeleteObserver" not in text


def test_renderer_script_clears_focus_and_removes_deleted_rows():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    assert "removeDeletedRow(row, button, ref)" in text
    assert "releaseDeleteFocus(row, button)" in text
    assert "button.blur()" in text
    assert "document.activeElement.blur()" in text
    assert "row.remove()" in text
    assert "row.style.display = \"none\"" not in text


def test_renderer_script_uses_in_page_confirm_and_stops_early_pointer_events():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    assert "confirm(" not in text
    assert "codex-delete-confirm-overlay" in text
    assert "escapeHtml(title)" in text
    assert "stopImmediatePropagation" in text
    assert "\"pointerdown\", \"mousedown\", \"mouseup\", \"touchstart\"" in text


def test_renderer_script_reloads_after_deleting_current_session():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    assert "isCurrentSessionRow" in text
    assert "window.location.href.includes(ref.session_id)" in text
    assert "window.location.reload()" in text


def test_renderer_script_toast_does_not_capture_page_interactions():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    assert "z-index: 2147483000" in text
    assert "pointer-events: none" in text
    assert "pointer-events: auto" in text




def test_renderer_script_supports_archived_conversation_delete_actions():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    assert "archivedSessionRows" in text
    assert "installArchivedDeleteAllButton" in text
    assert "删除全部归档" in text
    assert "deleteArchivedSessions" in text
    assert "data-codex-archive-delete-all" in text
    assert "data-app-action-sidebar-thread-id" in text
    assert "归档" in text


def test_renderer_script_adds_codex_plus_menu_with_feature_toggles():
    text = Path("codex_session_delete/inject/renderer-inject.js").read_text(encoding="utf-8")
    assert "installCodexPlusMenu" in text
    assert "Codex++" in text
    assert "插件选项解锁" in text
    assert "特殊插件强制安装" in text
    assert "会话删除" in text
    assert "关于 Codex++" in text
    assert "https://github.com/BigPizzaV3/CodexPlusPlus" in text
    assert "codexPlusSettings" in text
    assert "pluginEntryUnlock" in text
    assert "forcePluginInstall" in text
    assert "sessionDelete" in text
    assert "codex-plus-modal-overlay" in text
    assert "codex-plus-modal-content" in text
    assert "codex-plus-modal-header" in text
    assert "codex-dialog-overlay" not in text
    assert "bg-token-dropdown-background/90" not in text
    assert "backdrop-blur-xl" not in text
    assert "codex-plus-menu-floating" in text
    assert "findNativeMenuInsertionPoint" in text
    assert "app-header-tint" in text
    assert "flex items-center gap-0.5" in text
    assert "codex-plus-menu-floating" in text
    assert "nativeButtonClass" in text
    assert "removeDuplicateCodexPlusMenus" in text
    assert "data-codex-plus-menu" in text
    assert "textContent || \"\").trim() === \"Codex++\"" in text
    assert "codexPlusMenuVersion = \"5\"" in text
    assert "codexPlusTriggerInstalled = \"5\"" in text
    assert ".codex-plus-trigger:hover" not in text
