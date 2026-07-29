"""Shared utilities for Clang tools."""

import html
import os
import re
from datetime import datetime

from vnvtoolkit import get_function_impl_path, get_setting

# ── Settings helpers ──────────────────────────────────────────────────────────


def get_clang_format_command(settings):
    """Get the clang-format command from settings."""
    return str(get_setting(settings, "Clang-Format command", "clang-format"))


def get_clang_tidy_command(settings):
    """Get the clang-tidy command from settings."""
    return str(get_setting(settings, "Clang-Tidy command", "clang-tidy"))


def _split_setting_list(value):
    """Splits a ':'-separated setting string into a list, stripping empties."""
    return [item.strip() for item in str(value).split(":") if item.strip()]


def get_clang_tidy_include_paths(settings):
    """Get the clang-tidy include paths from settings (':'-separated list)."""
    return _split_setting_list(
        get_setting(settings, "Clang-Tidy include paths", "work/dataview/C")
    )


def get_clang_tidy_defines(settings):
    """Get the clang-tidy defines from settings (':'-separated list)."""
    return _split_setting_list(get_setting(settings, "Clang-Tidy defines", ""))


def build_clang_tidy_extra_args(include_paths, defines):
    """Builds a list of '--extra-arg' switches for clang-tidy.

    Each include path becomes '--extra-arg=-I<path>' and each define becomes
    '--extra-arg=-D<define>' (defines may be plain 'NAME' or 'NAME=VALUE').
    """
    extra_args = [f"--extra-arg=-I{path}" for path in include_paths]
    extra_args.extend(f"--extra-arg=-D{define}" for define in defines)
    return extra_args


# ── Config files helpers ──────────────────────────────────────────────────────────


def get_clang_format_file_path(project_directory):
    """Get the path to the .clang-format in the project directory."""
    return os.path.join(project_directory, ".clang-format") if project_directory else ""


def get_clang_style_file_path(project_directory):
    """Get the path to the .clang-tidy.style in the project directory."""
    return os.path.join(project_directory, ".clang-tidy.style") if project_directory else ""


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


def check_clang_style_file_exists(file_path):
    """
    Check if .clang-tidy.style exists.
    Returns (exists: bool, error_message: str or None).
    """
    if not file_path:
        return False, "Project directory is not configured"
    if not os.path.isfile(file_path):
        return (
            False,
            f".clang-tidy.style not found: {file_path}\nRun the 'Initialize Clang-Tidy (code style) configuration' tool first.",
        )
    return True, None


# ── Source file enumeration ───────────────────────────────────────────────────

SOURCE_EXTENSIONS = (".c", ".cpp", ".cc", ".h", ".hpp", ".hh")


def enumerate_source_files(project_directory, functions):
    """Collects source/header files (recursively) from each function's impl dir,
    skipping the function's own top-level generated header (<function_name>.h)."""
    source_files = []
    for fun in functions:
        source_dir = get_function_impl_path(project_directory, fun)
        if not source_dir:
            continue
        skip_file = f"{fun}.h"
        for root, dirs, entries in os.walk(source_dir):
            dirs.sort()
            for entry in sorted(entries):
                if not entry.lower().endswith(SOURCE_EXTENSIONS):
                    continue
                if root == source_dir and entry == skip_file:
                    continue
                source_files.append(os.path.join(root, entry))
    return source_files


# ── Issue message helpers ─────────────────────────────────────────────────────


def strip_trailing_bracket_suffix(message):
    """Strip a trailing bracketed suffix like [-Wfoo] or [some-check-name] from a message.

    Clang tools emit a constant check/flag identifier at the end of each
    diagnostic (e.g. [-Wclang-format-violations] or [readability-identifier-naming]).
    Since it's identical for every issue in a single-check run, stripping it
    reduces visual noise in the report.
    """
    return re.sub(r"\s*\[[^\]]+\]\s*$", "", message)


# ── HTML report scaffold ──────────────────────────────────────────────────────

_TOGGLE_SCRIPT = """
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("tr.summary-row").forEach(function (row) {
    row.addEventListener("click", function () {
      var detailsRow = row.nextElementSibling;
      if (!detailsRow || !detailsRow.classList.contains("details-row")) {
        return;
      }
      var expanded = detailsRow.classList.toggle("expanded");
      row.classList.toggle("expanded", expanded);
      var marker = row.querySelector(".toggle-marker");
      if (marker) {
        marker.textContent = expanded ? "\u2212" : "+";
      }
    });
  });
});
"""

_REPORT_CSS = """
body { font-family: sans-serif; margin: 24px; color: #222; }
h1 { margin-bottom: 0.25rem; }
h2 { margin: 2rem 0 0.75rem; }
table { border-collapse: collapse; width: 100%; margin-bottom: 1rem; }
th, td { border: 1px solid #ccc; padding: 8px; text-align: left; vertical-align: top; }
.summary-row { cursor: pointer; }
.summary-row.issue { background-color: #ffe5e5; }
tr.ok { background-color: #e5ffe5; }
.details-row { display: none; }
.details-row.expanded { display: table-row; }
.toggle-marker { display: inline-block; width: 1.2em; font-weight: bold; }
.stats { display: flex; gap: 16px; flex-wrap: wrap; margin: 1rem 0 1.5rem; }
.stat-card { min-width: 180px; padding: 16px; border: 1px solid #ddd; border-radius: 10px; background: #fafafa; }
.stat-label { font-size: 0.9rem; color: #666; margin-bottom: 6px; }
.stat-value { font-size: 2rem; font-weight: 700; line-height: 1; }
.stat-meta { margin-top: 6px; color: #666; }
.issue-block { border: 1px solid #ddd; border-radius: 8px; padding: 12px; margin: 10px 0; background: #fff; }
.issue-block-empty { color: #666; }
.issue-title { font-size: 0.9rem; font-weight: 700; color: #555; margin-bottom: 4px; }
.issue-message { margin-bottom: 8px; }
.issue-snippet { white-space: pre-wrap; margin: 0; padding: 10px; background: #f8f8f8; border-radius: 6px; border: 1px solid #eee; }
"""


def render_style_report_html(
    project_name,
    generated_at,
    total_files,
    files_with_issues,
    failure_rows_html,
    success_rows_html,
    category_label,
):
    """Render a full HTML code-style report page.

    Args:
        project_name: The project name shown in the title and heading.
        generated_at: Timestamp string to show under the heading.
        total_files: Total number of files processed.
        files_with_issues: Number of files with detected issues.
        failure_rows_html: Pre-rendered HTML rows for files with issues (may be empty string).
        success_rows_html: Pre-rendered HTML rows for verified files (may be empty string).
        category_label: Short label like "formatting" or "naming" used in all titles/headers.
    """
    files_without_issues = total_files - files_with_issues
    issue_percent = (files_with_issues / total_files * 100) if total_files else 0
    ok_percent = (files_without_issues / total_files * 100) if total_files else 0
    label_cap = category_label.capitalize()

    report = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{html.escape(project_name)} Code Style ({html.escape(category_label)}) Report</title>
<style>{_REPORT_CSS}</style>
<script>{_TOGGLE_SCRIPT}</script>
</head>
<body>
<h1>{html.escape(project_name)} Code Style ({html.escape(category_label)}) Report</h1>
<p>Generated {html.escape(generated_at)}</p>
<div class="stats">
  <div class="stat-card">
    <div class="stat-label">Processed files</div>
    <div class="stat-value">{total_files}</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">{html.escape(label_cap)} verified</div>
    <div class="stat-value">{files_without_issues}</div>
    <div class="stat-meta">{ok_percent:.1f}%</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">{html.escape(label_cap)} violations</div>
    <div class="stat-value">{files_with_issues}</div>
    <div class="stat-meta">{issue_percent:.1f}%</div>
  </div>
</div>
"""

    if failure_rows_html:
        report += f"""
<h2>Code Style ({html.escape(category_label)}) violations</h2>
<table>
<thead><tr><th>File</th><th>Summary</th></tr></thead>
<tbody>
{failure_rows_html}
</tbody>
</table>
"""

    if success_rows_html:
        report += f"""
<h2>Code Style ({html.escape(category_label)}) verified</h2>
<table>
<thead><tr><th>File</th><th>Summary</th></tr></thead>
<tbody>
{success_rows_html}
</tbody>
</table>
"""

    report += """
</body>
</html>
"""
    return report
