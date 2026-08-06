import html
import os
import re
import subprocess
from collections import Counter
from datetime import datetime

from clangshared import (
    build_clang_tidy_extra_args,
    enumerate_source_files,
    extract_trailing_bracket_suffix,
    get_check_category,
    get_clang_tidy_analysis_file_path,
    get_clang_tidy_command,
    get_clang_tidy_defines,
    get_clang_tidy_include_paths,
    render_analysis_report_html,
    render_check_badge,
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


def check_file_analysis(
    tidy_command, config_path, extra_args, project_directory, source_file
):
    """Runs clang-tidy on a single file and returns (has_issues, issues).

    Only issues originating from source_file itself are returned — diagnostics
    from included headers are discarded. Each issue dict includes a 'check' key
    with the check name extracted from the trailing bracketed suffix.
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
    all_issues = parse_analysis_issues(raw_output)
    issues = [i for i in all_issues if os.path.abspath(i["file"]) == source_file_abs]
    has_issues = bool(issues)
    return has_issues, issues


def parse_analysis_issues(issues_output):
    """Splits clang-tidy output into separate issue blocks.

    Each returned dict includes:
      'file', 'line', 'column', 'severity', 'message', 'check', 'body'.

    The trailing bracketed check name (e.g. [readability-magic-numbers]) is
    preserved as 'check' instead of being stripped, so the report can display
    it as a styled badge.
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
            clean_message, check_name = extract_trailing_bracket_suffix(message)
            current_issue = {
                "file": file_path,
                "line": line_no,
                "column": column_no,
                "severity": severity,
                "message": clean_message,
                "check": check_name,
                "body": [],
            }
        elif current_issue is not None:
            current_issue["body"].append(line)

    if current_issue is not None:
        issues.append(current_issue)

    return issues


def render_analysis_issues_html(issues):
    """Renders expanded issue details for a single file, with check-name badges."""
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
        badge_html = render_check_badge(issue.get("check"))
        rendered_issues.append(
            '<div class="issue-block">'
            f'<div class="issue-title">{html.escape(severity_label)} — '
            f"Line {html.escape(issue['line'])}, col {html.escape(issue['column'])}"
            f"{badge_html}</div>"
            f"<div class=\"issue-message\">{html.escape(issue['message'])}</div>"
            f"{body_html}"
            "</div>"
        )

    if not rendered_issues:
        rendered_issues.append(
            '<div class="issue-block issue-block-empty">No analysis details available.</div>'
        )

    return "".join(rendered_issues)


def render_analysis_report_row(project_directory, source_file, has_issues, issues):
    """Renders a table row for a processed source file."""
    rel_path = os.path.relpath(source_file, project_directory)
    if has_issues:
        issue_count = len(issues)
        details_html = render_analysis_issues_html(issues)
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
        f'<tr class="ok">' f"<td>{html.escape(rel_path)}</td>" "<td>Clean</td>" "</tr>"
    )


def render_check_summary_rows(all_issues):
    """Renders per-check count rows sorted by descending count."""
    check_counts = Counter(
        issue.get("check") or "unknown"
        for _, has_issues, issues in all_issues
        if has_issues
        for issue in issues
    )
    if not check_counts:
        return ""
    rows = []
    for check_name, count in sorted(check_counts.items(), key=lambda x: -x[1]):
        category = get_check_category(check_name)
        badge_html = render_check_badge(check_name)
        rows.append(
            f"<tr><td>{badge_html}</td>"
            f"<td>{html.escape(category)}</td>"
            f"<td>{count}</td></tr>"
        )
    return "".join(rows)


def generate_html_report(project_name, project_directory, results):
    """Generates the full HTML static analysis report for the given per-file results."""
    total_files = len(results)
    files_with_issues = sum(1 for _, has_issues, _ in results if has_issues)
    total_issues = sum(len(issues) for _, has_issues, issues in results if has_issues)
    generated_at = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")

    failure_rows_html = "".join(
        render_analysis_report_row(project_directory, source_file, has_issues, issues)
        for source_file, has_issues, issues in results
        if has_issues
    )
    success_rows_html = "".join(
        render_analysis_report_row(project_directory, source_file, has_issues, issues)
        for source_file, has_issues, issues in results
        if not has_issues
    )
    check_summary_rows_html = render_check_summary_rows(results)

    return render_analysis_report_html(
        project_name=project_name,
        generated_at=generated_at,
        total_files=total_files,
        files_with_issues=files_with_issues,
        total_issues=total_issues,
        failure_rows_html=failure_rows_html,
        success_rows_html=success_rows_html,
        check_summary_rows_html=check_summary_rows_html,
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
        output_filename = f"{project_name}-code-analysis-report.html"

        resolved_output = (
            resolve_path(taste_project_directory, output_directory)
            if output_directory
            else os.path.join(taste_project_directory, "output")
        )
        output_path = os.path.join(resolved_output, output_filename)

        config_path = get_clang_tidy_analysis_file_path(taste_project_directory)

        functions = get_leaf_function_names(
            get_interface_view_path(taste_project_directory)
        )
        source_files = enumerate_source_files(taste_project_directory, functions)

        emit_progress(10)

        results = []
        total_files = len(source_files)
        for index, source_file in enumerate(source_files):
            has_issues, issues = check_file_analysis(
                tidy_command,
                config_path,
                extra_args,
                taste_project_directory,
                source_file,
            )
            results.append((source_file, has_issues, issues))

            if total_files:
                emit_progress(10 + int((index + 1) / total_files * 85))

        emit_progress(95)

        content = generate_html_report(project_name, taste_project_directory, results)

        os.makedirs(resolved_output, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        emit_progress(100)

        status = "ok"
        status_text = f"Code analysis report created at: {output_path}"
        show_status = True

    except Exception as exc:
        status = "error"
        status_text = f"Failed to create code analysis report: {exc}"
        show_status = True
