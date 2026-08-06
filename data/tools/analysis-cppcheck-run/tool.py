import html
import json
import os
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime

from analysisshared import (
    enumerate_source_files,
    render_analysis_report_html,
    render_analysis_report_sarif,
    render_check_badge,
)
from cppcheckshared import (
    build_cppcheck_extra_args,
    build_enabled_groups,
    build_misra_addon_config,
    get_check_category,
    get_cppcheck_command,
    get_cppcheck_defines,
    get_cppcheck_include_paths,
    get_cppcheck_platform,
    get_cppcheck_version,
    get_misra_enabled,
    get_misra_rule_texts_path,
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


def parse_cppcheck_issues(xml_output):
    """Parse cppcheck --xml stderr output into issue dictionaries."""
    if not xml_output.strip():
        return []

    try:
        root = ET.fromstring(xml_output)
    except ET.ParseError as exc:
        raise RuntimeError(f"Failed to parse Cppcheck XML output: {exc}") from exc

    issues = []
    for error in root.findall(".//error"):
        locations = error.findall("location")
        primary_location = locations[0] if locations else None
        file_path = (
            (primary_location.get("file") if primary_location is not None else "")
            or error.get("file0")
            or ""
        )
        line_no = (
            primary_location.get("line", "1") if primary_location is not None else "1"
        )
        column_no = (
            primary_location.get("column", "1") if primary_location is not None else "1"
        )
        body = []
        for related in locations[1:]:
            rel_file = related.get("file", "")
            rel_line = related.get("line", "1")
            rel_column = related.get("column", "1")
            body.append(f"Related location: {rel_file}:{rel_line}:{rel_column}")

        symbol = error.findtext("symbol")
        if symbol:
            body.append(f"Symbol: {symbol}")

        issues.append(
            {
                "file": file_path,
                "line": str(line_no),
                "column": str(column_no),
                "severity": str(error.get("severity", "warning")).lower(),
                "message": error.get("msg") or error.get("verbose") or "",
                "check": error.get("id"),
                "body": body,
            }
        )
    return issues


def check_file_analysis(
    cppcheck_command,
    extra_args,
    enabled_groups,
    project_directory,
    source_file,
    addon_config_path=None,
):
    """Run Cppcheck for a single file and return (has_issues, issues)."""
    command = [cppcheck_command, "--xml", "--quiet"]
    if enabled_groups:
        command.append(f"--enable={','.join(enabled_groups)}")
    if addon_config_path:
        command.append(f"--addon={addon_config_path}")
    command.extend(extra_args)
    command.append(source_file)

    completed = subprocess.run(
        command,
        cwd=project_directory,
        capture_output=True,
        text=True,
        check=False,
    )

    issues = parse_cppcheck_issues(completed.stderr or "")
    source_file_abs = os.path.abspath(os.path.join(project_directory, source_file))
    filtered_issues = [
        issue
        for issue in issues
        if os.path.abspath(issue.get("file", "")) == source_file_abs
    ]
    return bool(filtered_issues), filtered_issues


def render_analysis_issues_html(issues):
    """Render expanded issue details for a single file."""
    rendered_issues = []

    for issue in issues:
        body_html = ""
        if issue["body"]:
            body_html = (
                '<pre class="issue-snippet">'
                f"{html.escape(os.linesep.join(issue['body']))}"
                "</pre>"
            )

        severity = issue.get("severity", "other")
        severity_label = severity.capitalize()
        category = get_check_category(issue.get("check"), severity)
        badge_html = render_check_badge(issue.get("check"), category)
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
    """Render one report table row for a processed source file."""
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
    """Render per-rule issue counts sorted by descending count."""
    check_counts = Counter(
        issue.get("check") or "cppcheck"
        for _, has_issues, issues in all_issues
        if has_issues
        for issue in issues
    )
    if not check_counts:
        return ""

    check_categories = {}
    for _, has_issues, issues in all_issues:
        if not has_issues:
            continue
        for issue in issues:
            check_name = issue.get("check") or "cppcheck"
            check_categories.setdefault(
                check_name,
                get_check_category(check_name, issue.get("severity", "other")),
            )

    rows = []
    for check_name, count in sorted(check_counts.items(), key=lambda item: -item[1]):
        category = check_categories.get(check_name, "other")
        badge_html = render_check_badge(check_name, category)
        rows.append(
            f"<tr><td>{badge_html}</td>"
            f"<td>{html.escape(category)}</td>"
            f"<td>{count}</td></tr>"
        )
    return "".join(rows)


def generate_html_report(
    project_name, project_directory, results, tool_version=None, sarif_filename=None
):
    """Generate the full Cppcheck HTML analysis report."""
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
        tool_name="Cppcheck",
        tool_version=tool_version,
        sarif_filename=sarif_filename,
    )


cppcheck_command = get_cppcheck_command(settings)
extra_args = build_cppcheck_extra_args(
    get_cppcheck_include_paths(settings),
    get_cppcheck_defines(settings),
    get_cppcheck_platform(settings),
)
enabled_groups = build_enabled_groups(settings)
misra_enabled = get_misra_enabled(settings)

if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
    show_status = True
else:
    misra_rule_texts_path = get_misra_rule_texts_path(settings, taste_project_directory)
    if misra_enabled and misra_rule_texts_path and not os.path.isfile(misra_rule_texts_path):
        status = "error"
        status_text = f"MISRA rule texts file not found: {misra_rule_texts_path}"
        show_status = True
    else:
        addon_config_path = None
        try:
            emit_progress(5)

            # Cppcheck reports MISRA addon findings with severity='style' and
            # silently drops them unless 'style' is in the active --enable=
            # set. Force 'style' into the effective invocation whenever the
            # MISRA addon is on, regardless of the "Enable style checks"
            # toggle, so MISRA findings are never silently suppressed. This
            # only affects the cppcheck invocation itself — report
            # categorization still relies on each issue's own check id.
            effective_groups = list(enabled_groups)
            if misra_enabled and "style" not in effective_groups:
                effective_groups.append("style")

            if misra_enabled:
                addon_config = build_misra_addon_config(misra_rule_texts_path)
                addon_fd, addon_config_path = tempfile.mkstemp(
                    suffix=".json", prefix="misra-addon-"
                )
                with os.fdopen(addon_fd, "w", encoding="utf-8") as f:
                    json.dump(addon_config, f)

            project_name = get_project_name(taste_project_directory)
            output_filename = f"{project_name}-cppcheck-report.html"
            sarif_output_filename = f"{project_name}-cppcheck-report.sarif"

            resolved_output = (
                resolve_path(taste_project_directory, output_directory)
                if output_directory
                else os.path.join(taste_project_directory, "output")
            )
            output_path = os.path.join(resolved_output, output_filename)
            sarif_output_path = os.path.join(resolved_output, sarif_output_filename)

            functions = get_leaf_function_names(
                get_interface_view_path(taste_project_directory)
            )
            source_files = enumerate_source_files(taste_project_directory, functions)

            emit_progress(10)

            results = []
            total_files = len(source_files)
            for index, source_file in enumerate(source_files):
                has_issues, issues = check_file_analysis(
                    cppcheck_command,
                    extra_args,
                    effective_groups,
                    taste_project_directory,
                    source_file,
                    addon_config_path=addon_config_path,
                )
                results.append((source_file, has_issues, issues))

                if total_files:
                    emit_progress(10 + int((index + 1) / total_files * 85))

            emit_progress(95)

            tool_version = get_cppcheck_version(cppcheck_command)

            content = generate_html_report(
                project_name,
                taste_project_directory,
                results,
                tool_version=tool_version,
                sarif_filename=sarif_output_filename,
            )
            sarif_content = render_analysis_report_sarif(
                project_directory=taste_project_directory,
                results=results,
                tool_name="cppcheck",
                tool_information_uri="https://cppcheck.sourceforge.io/",
                tool_version=tool_version,
                default_rule_id="cppcheck",
            )

            os.makedirs(resolved_output, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            with open(sarif_output_path, "w", encoding="utf-8") as f:
                f.write(sarif_content)

            emit_progress(100)

            status = "ok"
            status_text = (
                f"Cppcheck analysis report created at: {output_path} "
                f"(SARIF: {sarif_output_path})"
            )
            show_status = True

        except Exception as exc:
            status = "error"
            status_text = f"Failed to create Cppcheck analysis report: {exc}"
            show_status = True
        finally:
            if addon_config_path and os.path.isfile(addon_config_path):
                os.remove(addon_config_path)
