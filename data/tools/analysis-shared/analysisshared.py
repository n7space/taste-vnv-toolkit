"""Shared utilities for static-analysis tools."""

import html
import json
import os
import re

from vnvtoolkit import get_function_impl_path


def split_setting_list(value):
    """Split a ':'-separated setting string into a non-empty trimmed list."""
    return [item.strip() for item in str(value).split(":") if item.strip()]


SOURCE_EXTENSIONS = (".c", ".cpp", ".cc", ".h", ".hpp", ".hh")


def enumerate_source_files(project_directory, functions):
    """Collect source/header files from each function implementation directory."""
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


_CATEGORY_COLORS = {
    "quality": ("#1a4a8a", "#ddeeff"),
    "security": ("#7a0000", "#ffe0e0"),
    "best-practice": ("#2a6a00", "#e0f5d0"),
    "error": ("#7a0000", "#ffe0e0"),
    "warning": ("#8a5a00", "#fff0cc"),
    "style": ("#1a4a8a", "#ddeeff"),
    "performance": ("#5e2b97", "#efe3ff"),
    "portability": ("#00706b", "#d8f7f5"),
    "information": ("#555555", "#f0f0f0"),
    "misra": ("#8a3a00", "#ffe6cc"),
    "other": ("#555555", "#f0f0f0"),
}


def render_check_badge(check_name, category="other"):
    """Render a small HTML badge for the given check/rule identifier."""
    if not check_name:
        return ""
    category = category or "other"
    if category not in _CATEGORY_COLORS:
        category = "other"
    return (
        f"<span class=\"check-badge check-badge-{html.escape(category)}\" "
        f"title=\"Category: {html.escape(category)}\">"
        f"{html.escape(check_name)}</span>"
    )


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
        marker.textContent = expanded ? "\\u2212" : "+";
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
.check-badge { display: inline-block; font-size: 0.75rem; font-family: monospace; padding: 2px 7px; border-radius: 4px; margin-left: 6px; vertical-align: middle; font-weight: 600; }
.check-badge-quality { color: #1a4a8a; background: #ddeeff; border: 1px solid #aaccee; }
.check-badge-security { color: #7a0000; background: #ffe0e0; border: 1px solid #ffaaaa; }
.check-badge-best-practice { color: #2a6a00; background: #e0f5d0; border: 1px solid #99dd77; }
.check-badge-error { color: #7a0000; background: #ffe0e0; border: 1px solid #ffaaaa; }
.check-badge-warning { color: #8a5a00; background: #fff0cc; border: 1px solid #ffd27a; }
.check-badge-style { color: #1a4a8a; background: #ddeeff; border: 1px solid #aaccee; }
.check-badge-performance { color: #5e2b97; background: #efe3ff; border: 1px solid #ccb3ff; }
.check-badge-portability { color: #00706b; background: #d8f7f5; border: 1px solid #9de5df; }
.check-badge-information { color: #555555; background: #f0f0f0; border: 1px solid #cccccc; }
.check-badge-misra { color: #8a3a00; background: #ffe6cc; border: 1px solid #ffc78a; }
.check-badge-other { color: #555555; background: #f0f0f0; border: 1px solid #cccccc; }
.sarif-link { display: inline-block; margin: 0.5rem 0 1rem; padding: 8px 16px; background: #1a4a8a; color: #fff; text-decoration: none; border-radius: 6px; font-size: 0.9rem; font-weight: 600; }
.sarif-link:hover { background: #123a6e; }
"""


def render_analysis_report_html(
    project_name,
    generated_at,
    total_files,
    files_with_issues,
    total_issues,
    failure_rows_html,
    success_rows_html,
    check_summary_rows_html,
    tool_name=None,
    tool_version=None,
    sarif_filename=None,
):
    """Render a full HTML static-analysis report page."""
    files_without_issues = total_files - files_with_issues
    issue_percent = (files_with_issues / total_files * 100) if total_files else 0
    ok_percent = (files_without_issues / total_files * 100) if total_files else 0

    version_suffix = ""
    if tool_version and tool_name:
        version_suffix = (
            f" using {html.escape(tool_name)} {html.escape(str(tool_version))}"
        )
    elif tool_version:
        version_suffix = f" using {html.escape(str(tool_version))}"

    sarif_link_html = ""
    if sarif_filename:
        sarif_link_html = (
            f'<a class="sarif-link" href="{html.escape(sarif_filename)}" download>'
            "Download SARIF report</a>"
        )

    report = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{html.escape(project_name)} Static Analysis Report</title>
<style>{_REPORT_CSS}</style>
<script>{_TOGGLE_SCRIPT}</script>
</head>
<body>
<h1>{html.escape(project_name)} Static Analysis Report</h1>
<p>Generated {html.escape(generated_at)}{version_suffix}</p>
{sarif_link_html}
<div class="stats">
  <div class="stat-card">
    <div class="stat-label">Processed files</div>
    <div class="stat-value">{total_files}</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Clean files</div>
    <div class="stat-value">{files_without_issues}</div>
    <div class="stat-meta">{ok_percent:.1f}%</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Files with issues</div>
    <div class="stat-value">{files_with_issues}</div>
    <div class="stat-meta">{issue_percent:.1f}%</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Total findings</div>
    <div class="stat-value">{total_issues}</div>
  </div>
</div>
"""

    if check_summary_rows_html:
        report += f"""
<h2>Issues by check</h2>
<table>
<thead><tr><th>Check</th><th>Category</th><th>Count</th></tr></thead>
<tbody>
{check_summary_rows_html}
</tbody>
</table>
"""

    if failure_rows_html:
        report += f"""
<h2>Files with issues</h2>
<table>
<thead><tr><th>File</th><th>Summary</th></tr></thead>
<tbody>
{failure_rows_html}
</tbody>
</table>
"""

    if success_rows_html:
        report += f"""
<h2>Clean files</h2>
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


_SEMANTIC_VERSION_RE = re.compile(r"^[0-9]+(?:\.[0-9]+){1,3}$")

_DEFAULT_SARIF_LEVEL_BY_SEVERITY = {
    "error": "error",
    "warning": "warning",
    "style": "warning",
    "performance": "warning",
    "portability": "warning",
    "information": "note",
}


def render_analysis_report_sarif(
    project_directory,
    results,
    tool_name,
    tool_information_uri,
    tool_version,
    default_rule_id="analysis",
    severity_level_map=None,
):
    """Render a SARIF 2.1.0 log (as JSON text) for static-analysis results."""
    sarif_results = []
    level_map = severity_level_map or _DEFAULT_SARIF_LEVEL_BY_SEVERITY

    for source_file, has_issues, issues in results:
        if not has_issues:
            continue
        rel_path = os.path.relpath(source_file, project_directory).replace(os.sep, "/")
        for issue in issues:
            rule_id = issue.get("check") or default_rule_id
            level = level_map.get(issue.get("severity"), "warning")

            try:
                start_line = int(issue["line"])
            except (KeyError, TypeError, ValueError):
                start_line = 1
            try:
                start_column = int(issue["column"])
            except (KeyError, TypeError, ValueError):
                start_column = 1
            if start_column <= 0:
                # SARIF requires startColumn >= 1, so clamp to the start of the line.
                start_column = 1

            sarif_results.append(
                {
                    "ruleId": rule_id,
                    "level": level,
                    "message": {"text": issue.get("message", "")},
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {"uri": rel_path},
                                "region": {
                                    "startLine": start_line,
                                    "startColumn": start_column,
                                },
                            }
                        }
                    ],
                }
            )

    driver = {
        "name": tool_name,
        "informationUri": tool_information_uri,
        "version": tool_version,
    }
    if _SEMANTIC_VERSION_RE.match(str(tool_version)):
        driver["semanticVersion"] = str(tool_version)

    sarif_log = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {"driver": driver},
                "results": sarif_results,
            }
        ],
    }

    return json.dumps(sarif_log, indent=2)
