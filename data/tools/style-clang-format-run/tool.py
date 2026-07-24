import html
import os
import subprocess

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


def render_report_row(project_directory, source_file, has_issues, issues_output):
    """Renders a single HTML table row for a processed source file."""
    rel_path = os.path.relpath(source_file, project_directory)
    if has_issues:
        return (
            "<tr class=\"issue\">"
            f"<td>{html.escape(rel_path)}</td>"
            "<td>Issues found</td>"
            f"<td><pre>{html.escape(issues_output)}</pre></td>"
            "</tr>"
        )
    return (
        "<tr class=\"ok\">"
        f"<td>{html.escape(rel_path)}</td>"
        "<td>OK</td>"
        "<td></td>"
        "</tr>"
    )


def generate_html_report(project_name, project_directory, results):
    """Generates the full HTML code style report for the given per-file results."""
    total_files = len(results)
    files_with_issues = sum(1 for _, has_issues, _ in results if has_issues)
    rows = [
        render_report_row(project_directory, source_file, has_issues, issues_output)
        for source_file, has_issues, issues_output in results
    ]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{html.escape(project_name)} Code Style Report</title>
<style>
body {{ font-family: sans-serif; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; vertical-align: top; }}
tr.issue {{ background-color: #ffe5e5; }}
tr.ok {{ background-color: #e5ffe5; }}
pre {{ white-space: pre-wrap; margin: 0; }}
</style>
</head>
<body>
<h1>{html.escape(project_name)} Code Style Report</h1>
<p>Processed {total_files} file(s), {files_with_issues} with issues.</p>
<table>
<thead><tr><th>File</th><th>Status</th><th>Details</th></tr></thead>
<tbody>
{''.join(rows)}
</tbody>
</table>
</body>
</html>
"""


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
