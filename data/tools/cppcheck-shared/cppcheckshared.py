"""Shared utilities for Cppcheck-based tools."""

import re
import subprocess

from analysisshared import split_setting_list
from vnvtoolkit import get_bool_setting, get_setting, resolve_path

CPPCHECK_CHECK_GROUPS = [
    ("Enable style checks", "style", True),
    ("Enable warning checks", "warning", True),
    ("Enable performance checks", "performance", True),
    ("Enable portability checks", "portability", True),
    ("Enable information messages", "information", True),
    ("Enable unused function checks", "unusedFunction", False),
    ("Enable missing include checks", "missingInclude", False),
]

_FALLBACK_CPPCHECK_VERSION = "0.0.0"
_CPPCHECK_VERSION_RE = re.compile(r"Cppcheck\s+([0-9]+(?:\.[0-9]+){1,3})")


def get_cppcheck_command(settings):
    """Get the cppcheck command from settings."""
    return str(get_setting(settings, "Cppcheck command", "cppcheck"))


def get_cppcheck_include_paths(settings):
    """Get cppcheck include paths from settings (':'-separated list)."""
    return split_setting_list(
        get_setting(settings, "Cppcheck include paths", "work/dataview/C")
    )


def get_cppcheck_defines(settings):
    """Get cppcheck defines from settings (':'-separated list)."""
    return split_setting_list(get_setting(settings, "Cppcheck defines", ""))


def get_cppcheck_platform(settings):
    """Get cppcheck platform identifier from settings."""
    return str(get_setting(settings, "Cppcheck platform", "unix64")).strip()


def build_cppcheck_extra_args(include_paths, defines, platform):
    """Build extra cppcheck switches for include paths, defines, and platform."""
    extra_args = [f"-I{path}" for path in include_paths]
    extra_args.extend(f"-D{define}" for define in defines)
    if platform:
        extra_args.append(f"--platform={platform}")
    return extra_args


def build_enabled_groups(settings):
    """Return enabled cppcheck groups from Bool settings."""
    enabled = []
    for setting_name, group_name, default in CPPCHECK_CHECK_GROUPS:
        if get_bool_setting(settings, setting_name, default):
            enabled.append(group_name)
    return enabled


def get_cppcheck_version(cppcheck_command):
    """Resolve cppcheck version string (e.g. '2.21.1')."""
    try:
        completed = subprocess.run(
            [cppcheck_command, "--version"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except Exception:
        return _FALLBACK_CPPCHECK_VERSION

    output = (completed.stdout or "") + (completed.stderr or "")
    match = _CPPCHECK_VERSION_RE.search(output)
    if not match:
        return _FALLBACK_CPPCHECK_VERSION
    return match.group(1)


def get_check_category(check_name, severity):
    """Map a cppcheck check id/severity pair to a report badge category.

    MISRA addon findings (check ids like 'misra-c2012-8.4') always get the
    'misra' category so they're visually distinguishable from cppcheck's own
    'style'-severity findings, even though cppcheck reports both with
    severity='style'.
    """
    if str(check_name or "").lower().startswith("misra-"):
        return "misra"
    value = str(severity or "").strip().lower()
    if value in {
        "error",
        "warning",
        "style",
        "performance",
        "portability",
        "information",
    }:
        return value
    return "other"


# ── MISRA C 2012 addon ────────────────────────────────────────────────────────


def get_misra_enabled(settings):
    """Whether the MISRA C 2012 addon should be enabled."""
    return get_bool_setting(settings, "Enable MISRA C 2012 addon", False)


def get_misra_rule_texts_path(settings, project_directory):
    """Resolve the configured MISRA rule texts file path, or None if unset.

    The MISRA C:2012 rule-texts file ('Appendix A - summary of guidelines')
    is a copyrighted document that must be supplied by the user under their
    own MISRA license; the toolkit never bundles it.
    """
    raw_path = str(get_setting(settings, "MISRA rule texts file", "")).strip()
    if not raw_path:
        return None
    return resolve_path(project_directory, raw_path)


def build_misra_addon_config(rule_texts_path=None):
    """Build the Cppcheck addon config dict enabling the MISRA C 2012 addon.

    Cppcheck addons are enabled via '--addon=<path-to-json>', where the JSON
    file has the shape {"script": "misra.py", "args": [...]}."""
    config = {"script": "misra.py"}
    if rule_texts_path:
        config["args"] = [f"--rule-texts={rule_texts_path}"]
    return config
