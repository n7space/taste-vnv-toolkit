import html
import os
import re
import subprocess
from datetime import datetime

from clangshared import get_clang_format_command
from vnvtoolkit import (
    get_function_impl_path,
    get_interface_view_path,
    get_leaf_function_names,
    get_project_name,
    resolve_path,
)

SOURCE_EXTENSIONS = (".c", ".cpp", ".cc", ".h", ".hpp", ".hh")


def emit_progress(value):
    if "report_progress" in globals():
        report_progress(value)


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


def check_file_format(format_command, project_directory, source_file):
    """Runs clang-format --dry-run on a single file and returns (has_issues, output)."""
    completed = subprocess.run(
        [format_command, "--style=file", "--dry-run", "--Werror", source_file],
        cwd=project_directory,
        capture_output=True,
        text=True,
        check=False,
    )
    has_issues = completed.returncode != 0
    issues_output = (completed.stdout or "") + (completed.stderr or "")
    return has_issues, issues_output.strip()


def parse_format_issues(issues_output):
    """Splits clang-format output into separate issue blocks."""
    issue_header = re.compile(r"^(.*?):(\d+):(\d+): error: (.+)$")
    issues = []
    current_issue = None

    for line in issues_output.splitlines():
        match = issue_header.match(line)
        if match:
            if current_issue is not None:
                issues.append(current_issue)
            _, line_no, column_no, message = match.groups()
            message = re.sub(r"\s*\[-W[\w-]+\]\s*$", "", message)
            current_issue = {
                "line": line_no,
                "column": column_no,
                "message": message,
                "body": [],
            }
        elif current_issue is not None:
            current_issue["body"].append(line)

    if current_issue is not None:
        issues.append(current_issue)

    return issues


def render_issues_html(issues_output):
    """Renders expanded issue details for a single file."""
    issues = parse_format_issues(issues_output)
    rendered_issues = []

    for issue in issues:
        body_html = ""
        if issue["body"]:
            body_html = (
                "<pre class=\"issue-snippet\">"
                f"{html.escape(os.linesep.join(issue['body']))}"
                "</pre>"
            )
        rendered_issues.append(
            "<div class=\"issue-block\">"
            f"<div class=\"issue-title\">Line {html.escape(issue['line'])}, col {html.escape(issue['column'])}</div>"
            f"<div class=\"issue-message\">{html.escape(issue['message'])}</div>"
            f"{body_html}"
            "</div>"
        )

    if not rendered_issues:
        rendered_issues.append(
            "<div class=\"issue-block issue-block-empty\">No formatting details available.</div>"
        )

    return "".join(rendered_issues)


def render_report_row(project_directory, source_file, has_issues, issues_output):
    """Renders a table row for a processed source file.

    Failure rows are collapsible (clickable summary + hidden details).
    Success rows are plain, non-interactive rows.
    """
    rel_path = os.path.relpath(source_file, project_directory)
    if has_issues:
        issue_count = len(parse_format_issues(issues_output))
        details_html = render_issues_html(issues_output)
        return (
            f"<tr class=\"summary-row issue\" data-summary-row=\"true\">"
            f"<td><span class=\"toggle-marker\">+</span> {html.escape(rel_path)}</td>"
            f"<td>Issues found ({issue_count})</td>"
            "</tr>"
            "<tr class=\"details-row issue\">"
            f"<td colspan=\"2\">{details_html}</td>"
            "</tr>"
        )
    return (
        f"<tr class=\"ok\">"
        f"<td>{html.escape(rel_path)}</td>"
        "<td>Verified</td>"
        "</tr>"
    )


def generate_html_report(project_name, project_directory, results):
    """Generates the full HTML code style report for the given per-file results."""
    total_files = len(results)
    files_with_issues = sum(1 for _, has_issues, _ in results if has_issues)
    files_without_issues = total_files - files_with_issues
    issue_percent = (files_with_issues / total_files * 100) if total_files else 0
    ok_percent = (files_without_issues / total_files * 100) if total_files else 0
    generated_at = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")

    failure_rows = [
        render_report_row(project_directory, source_file, has_issues, issues_output)
        for source_file, has_issues, issues_output in results
        if has_issues
    ]
    success_rows = [
        render_report_row(project_directory, source_file, has_issues, issues_output)
        for source_file, has_issues, issues_output in results
        if not has_issues
    ]

    report = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{html.escape(project_name)} Code Style (formatting) Report</title>
<style>
body {{ font-family: sans-serif; margin: 24px; color: #222; }}
h1 {{ margin-bottom: 0.25rem; }}
h2 {{ margin: 2rem 0 0.75rem; }}
table {{ border-collapse: collapse; width: 100%; margin-bottom: 1rem; }}
th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; vertical-align: top; }}
.summary-row {{ cursor: pointer; }}
.summary-row.issue {{ background-color: #ffe5e5; }}
tr.ok {{ background-color: #e5ffe5; }}
.details-row {{ display: none; }}
.details-row.expanded {{ display: table-row; }}
.toggle-marker {{ display: inline-block; width: 1.2em; font-weight: bold; }}
.stats {{ display: flex; gap: 16px; flex-wrap: wrap; margin: 1rem 0 1.5rem; }}
.stat-card {{ min-width: 180px; padding: 16px; border: 1px solid #ddd; border-radius: 10px; background: #fafafa; }}
.stat-label {{ font-size: 0.9rem; color: #666; margin-bottom: 6px; }}
.stat-value {{ font-size: 2rem; font-weight: 700; line-height: 1; }}
.stat-meta {{ margin-top: 6px; color: #666; }}
.issue-block {{ border: 1px solid #ddd; border-radius: 8px; padding: 12px; margin: 10px 0; background: #fff; }}
.issue-block-empty {{ color: #666; }}
.issue-title {{ font-size: 0.9rem; font-weight: 700; color: #555; margin-bottom: 4px; }}
.issue-message {{ margin-bottom: 8px; }}
.issue-snippet {{ white-space: pre-wrap; margin: 0; padding: 10px; background: #f8f8f8; border-radius: 6px; border: 1px solid #eee; }}
</style>
<script>
document.addEventListener("DOMContentLoaded", function () {{
  document.querySelectorAll("tr.summary-row").forEach(function (row) {{
    row.addEventListener("click", function () {{
      var detailsRow = row.nextElementSibling;
      if (!detailsRow || !detailsRow.classList.contains("details-row")) {{
        return;
      }}
      var expanded = detailsRow.classList.toggle("expanded");
      row.classList.toggle("expanded", expanded);
      var marker = row.querySelector(".toggle-marker");
      if (marker) {{
        marker.textContent = expanded ? "−" : "+";
      }}
    }});
  }});
}});
</script>
</head>
<body>
<h1>{html.escape(project_name)} Code Style (formatting) Report</h1>
<p>Generated {html.escape(generated_at)}</p>
<div class="stats">
  <div class="stat-card">
    <div class="stat-label">Processed files</div>
    <div class="stat-value">{total_files}</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Formatting verified</div>
    <div class="stat-value">{files_without_issues}</div>
    <div class="stat-meta">{ok_percent:.1f}%</div>
  </div>
  <div class="stat-card">
    <div class="stat-label">Formatting violations</div>
    <div class="stat-value">{files_with_issues}</div>
    <div class="stat-meta">{issue_percent:.1f}%</div>
  </div>
</div>
"""

    if failure_rows:
        report += f"""
<h2>Code Style (formatting) violations</h2>
<table>
<thead><tr><th>File</th><th>Summary</th></tr></thead>
<tbody>
{''.join(failure_rows)}
</tbody>
</table>
"""

    if success_rows:
        report += f"""
<h2>Code Style (formatting) verified</h2>
<table>
<thead><tr><th>File</th><th>Summary</th></tr></thead>
<tbody>
{''.join(success_rows)}
</tbody>
</table>
"""

    report += """
</body>
</html>
"""
    return report


format_command = get_clang_format_command(settings)

if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
    show_status = True
else:
    try:
        emit_progress(5)

        project_name = get_project_name(taste_project_directory)
        output_filename = f"{project_name}-code-style-report.html"

        resolved_output = (
            resolve_path(taste_project_directory, output_directory)
            if output_directory
            else os.path.join(taste_project_directory, "output")
        )
        output_path = os.path.join(resolved_output, output_filename)

        functions = get_leaf_function_names(
            get_interface_view_path(taste_project_directory)
        )
        source_files = enumerate_source_files(taste_project_directory, functions)

        emit_progress(10)

        results = []
        total_files = len(source_files)
        for index, source_file in enumerate(source_files):
            has_issues, issues_output = check_file_format(
                format_command, taste_project_directory, source_file
            )
            results.append((source_file, has_issues, issues_output))

            if total_files:
                emit_progress(10 + int((index + 1) / total_files * 85))

        emit_progress(95)

        content = generate_html_report(project_name, taste_project_directory, results)

        os.makedirs(resolved_output, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        emit_progress(100)

        status = "ok"
        status_text = f"Code style report created at: {output_path}"
        show_status = True

    except Exception as exc:
        status = "error"
        status_text = f"Failed to create code style report: {exc}"
        show_status = True
