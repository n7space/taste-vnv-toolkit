import html
import os
import re
import subprocess
from datetime import datetime

from clangshared import (
    build_clang_tidy_extra_args,
    enumerate_source_files,
    get_clang_style_file_path,
    get_clang_tidy_command,
    get_clang_tidy_defines,
    get_clang_tidy_include_paths,
    render_style_report_html,
    strip_trailing_bracket_suffix,
)
from vnvtoolkit import (
    get_interface_view_path,
    get_leaf_function_names,
    get_project_name,
    resolve_path,
)


def emit_progress(value):
    if "report_progress" in globals():
        report_progress(value)


def check_file_naming(
    tidy_command, config_path, extra_args, project_directory, source_file
):
    """Runs clang-tidy on a single file and returns (has_issues, issues).

    Only issues originating from source_file itself are returned — diagnostics
    from included headers are discarded. has_issues is determined by whether any
    such filtered issues exist, not by the process exit code.
    """
    completed = subprocess.run(
        [
            tidy_command,
            f"--config-file={config_path}",
            "--quiet",
            *extra_args,
            source_file,
            "--",
        ],
        cwd=project_directory,
        capture_output=True,
        text=True,
        check=False,
    )
    raw_output = ((completed.stdout or "") + (completed.stderr or "")).strip()
    source_file_abs = os.path.abspath(os.path.join(project_directory, source_file))
    all_issues = parse_tidy_issues(raw_output)
    issues = [i for i in all_issues if os.path.abspath(i["file"]) == source_file_abs]
    has_issues = bool(issues)
    return has_issues, issues


def parse_tidy_issues(issues_output):
    """Splits clang-tidy output into separate issue blocks.

    Each returned dict includes a 'file' key with the path from the diagnostic
    header line. The trailing bracketed check name (e.g.
    [readability-identifier-naming]) is stripped from each message.
    """
    issue_header = re.compile(r"^(.*?):(\d+):(\d+): (warning|error): (.+)$")
    issues = []
    current_issue = None

    for line in issues_output.splitlines():
        match = issue_header.match(line)
        if match:
            if current_issue is not None:
                issues.append(current_issue)
            file_path, line_no, column_no, severity, message = match.groups()
            message = strip_trailing_bracket_suffix(message)
            current_issue = {
                "file": file_path,
                "line": line_no,
                "column": column_no,
                "severity": severity,
                "message": message,
                "body": [],
            }
        elif current_issue is not None:
            current_issue["body"].append(line)

    if current_issue is not None:
        issues.append(current_issue)

    return issues


def render_issues_html(issues):
    """Renders expanded issue details for a single file."""
    rendered_issues = []

    for issue in issues:
        body_html = ""
        if issue["body"]:
            body_html = (
                '<pre class="issue-snippet">'
                f"{html.escape(os.linesep.join(issue['body']))}"
                "</pre>"
            )
        severity_label = issue["severity"].capitalize()
        rendered_issues.append(
            '<div class="issue-block">'
            f'<div class="issue-title">{html.escape(severity_label)} — '
            f"Line {html.escape(issue['line'])}, col {html.escape(issue['column'])}</div>"
            f"<div class=\"issue-message\">{html.escape(issue['message'])}</div>"
            f"{body_html}"
            "</div>"
        )

    if not rendered_issues:
        rendered_issues.append(
            '<div class="issue-block issue-block-empty">No naming details available.</div>'
        )

    return "".join(rendered_issues)


def render_report_row(project_directory, source_file, has_issues, issues):
    """Renders a table row for a processed source file.

    Failure rows are collapsible (clickable summary + hidden details).
    Success rows are plain, non-interactive rows.
    """
    rel_path = os.path.relpath(source_file, project_directory)
    if has_issues:
        issue_count = len(issues)
        details_html = render_issues_html(issues)
        return (
            f'<tr class="summary-row issue" data-summary-row="true">'
            f'<td><span class="toggle-marker">+</span> {html.escape(rel_path)}</td>'
            f"<td>Issues found ({issue_count})</td>"
            "</tr>"
            '<tr class="details-row issue">'
            f'<td colspan="2">{details_html}</td>'
            "</tr>"
        )
    return (
        f'<tr class="ok">'
        f"<td>{html.escape(rel_path)}</td>"
        "<td>Verified</td>"
        "</tr>"
    )


def generate_html_report(project_name, project_directory, results):
    """Generates the full HTML code style (naming) report for the given per-file results."""
    total_files = len(results)
    files_with_issues = sum(1 for _, has_issues, _ in results if has_issues)
    generated_at = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")

    failure_rows_html = "".join(
        render_report_row(project_directory, source_file, has_issues, issues_output)
        for source_file, has_issues, issues_output in results
        if has_issues
    )
    success_rows_html = "".join(
        render_report_row(project_directory, source_file, has_issues, issues_output)
        for source_file, has_issues, issues_output in results
        if not has_issues
    )

    return render_style_report_html(
        project_name=project_name,
        generated_at=generated_at,
        total_files=total_files,
        files_with_issues=files_with_issues,
        failure_rows_html=failure_rows_html,
        success_rows_html=success_rows_html,
        category_label="naming",
    )


tidy_command = get_clang_tidy_command(settings)
extra_args = build_clang_tidy_extra_args(
    get_clang_tidy_include_paths(settings), get_clang_tidy_defines(settings)
)

if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
    show_status = True
else:
    try:
        emit_progress(5)

        project_name = get_project_name(taste_project_directory)
        output_filename = f"{project_name}-code-naming-report.html"

        resolved_output = (
            resolve_path(taste_project_directory, output_directory)
            if output_directory
            else os.path.join(taste_project_directory, "output")
        )
        output_path = os.path.join(resolved_output, output_filename)

        config_path = get_clang_style_file_path(taste_project_directory)

        functions = get_leaf_function_names(
            get_interface_view_path(taste_project_directory)
        )
        source_files = enumerate_source_files(taste_project_directory, functions)

        emit_progress(10)

        results = []
        total_files = len(source_files)
        for index, source_file in enumerate(source_files):
            has_issues, issues_output = check_file_naming(
                tidy_command,
                config_path,
                extra_args,
                taste_project_directory,
                source_file,
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
        status_text = f"Code naming report created at: {output_path}"
        show_status = True

    except Exception as exc:
        status = "error"
        status_text = f"Failed to create code naming report: {exc}"
        show_status = True
