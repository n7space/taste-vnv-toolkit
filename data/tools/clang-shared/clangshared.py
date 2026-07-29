"""Shared utilities for Clang tools."""

import os

from vnvtoolkit import get_setting

# ── Settings helpers ──────────────────────────────────────────────────────────


def get_clang_format_command(settings):
    """Get the clang-format command from settings."""
    return str(get_setting(settings, "Clang-Format command", "clang-format"))


# ── Config files helpers ──────────────────────────────────────────────────────────


def get_clang_format_file_path(project_directory):
    """Get the path to the .clang-format in the project directory."""
    return os.path.join(project_directory, ".clang-format") if project_directory else ""


def check_clang_format_file_exists(file_path):
    """
    Check if .clang-format exists.
    Returns (exists: bool, error_message: str or None).
    """
    if not file_path:
        return False, "Project directory is not configured"
    if not os.path.isfile(file_path):
        return (
            False,
            f".clang-format not found: {file_path}\nRun the 'Initialize Clang-Format configuration' tool first.",
        )
    return True, None
