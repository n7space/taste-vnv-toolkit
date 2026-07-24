"""Generic utilities for all tools"""

import os
import shutil
import subprocess
import sys

# ── Settings helpers ──────────────────────────────────────────────────────────


def get_setting(settings, name, default_value):
    """Get a setting value by name, or return default if not found."""
    for setting_name, setting_value in settings:
        if setting_name == name:
            return setting_value
    return default_value


# ── Project helpers ───────────────────────────────────────────────────────────


def get_project_name(project_directory):
    """Extract project name from the project directory path."""
    if not project_directory:
        return "TASTE"
    return os.path.basename(os.path.abspath(project_directory))


# ── Commands helpers ──────────────────────────────────────────────────────────


def check_command_availability(command):
    """
    Check if givan command is available in PATH.
    Returns (status, status_text) tuple.
    """
    path = shutil.which(command)
    if path is not None:
        return "ok", f"{command} found at {path}"
    return "error", f"{command} not found in PATH"


# ── File/directory opening ────────────────────────────────────────────────────


def open_in_os_viewer(path):
    """
    Opens provided path using default OS action
    (e.g. file explorer for directories, Web browser for HTML files).
    """
    if sys.platform.startswith("win"):
        os.startfile(path)
        return

    command = ["open", path] if sys.platform == "darwin" else ["xdg-open", path]
    subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


# ── Path resolution utilities ─────────────────────────────────────────────────


def resolve_path(base_path, relative_or_absolute_path):
    """
    Resolve a path that may be relative or absolute.
    If absolute, return as-is. If relative, join with base_path.
    """
    if os.path.isabs(relative_or_absolute_path):
        return relative_or_absolute_path
    else:
        return os.path.join(base_path, relative_or_absolute_path)
