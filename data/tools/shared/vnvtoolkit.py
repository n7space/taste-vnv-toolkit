"""Generic utilities for all tools"""

import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

# ── Settings helpers ──────────────────────────────────────────────────────────


def get_setting(settings, name, default_value):
    """Get a setting value by name, or return default if not found."""
    for setting_name, setting_value in settings:
        if setting_name == name:
            return setting_value
    return default_value


def get_bool_setting(settings, name, default):
    """Get a boolean setting value by name, coercing strings to bool."""
    val = get_setting(settings, name, default)
    if isinstance(val, bool):
        return val
    return str(val).strip().lower() in ("true", "1", "yes")


def get_int_setting(settings, name, default):
    """Get an integer setting value by name, returning default on parse failure."""
    try:
        return int(get_setting(settings, name, default))
    except (TypeError, ValueError):
        return default


# ── Project helpers ───────────────────────────────────────────────────────────


def get_project_name(project_directory):
    """Extract project name from the project directory path."""
    if not project_directory:
        return "TASTE"
    return os.path.basename(os.path.abspath(project_directory))


def get_interface_view_path(project_directory):
    """Provides project's Interface View XML file path"""
    path = os.path.join(project_directory, "interfaceview.xml")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"interfaceview.xml not found: {path}")
    return path


def normalize_function_name(function_name):
    """Normalize functoion name for path processing"""
    return re.sub(r"\s+", "_", function_name.strip().lower())


def get_leaf_function_names(interfaceview_path, language="C"):
    """Lists all functions that have implementation in provided language"""
    tree = ET.parse(interfaceview_path)
    root = tree.getroot()

    # must be a leaf (no sub-functions) and in correct language
    functions = [
        fun
        for fun in root.findall(".//Function")
        if fun.find("Function") is None and fun.get("language").upper() == language
    ]
    names = [normalize_function_name(fun.get("name", "")) for fun in functions]
    return [name for name in sorted(set(names)) if name]


def get_function_impl_path(project_directory, function_name, language="C"):
    """Provides path to function implementation in specified language"""
    root = os.path.join(project_directory, "work", function_name)
    if not os.path.isdir(root):
        raise FileNotFoundError(
            f"Generated work directory not found for function '{function_name}': {root}"
        )

    impl_dir = os.path.join(root, language, "src")
    if not os.path.isdir(impl_dir):
        return ""

    return impl_dir


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
