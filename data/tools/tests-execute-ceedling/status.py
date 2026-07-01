import os
import shutil

from testsharedceedling import get_setting, parse_project_yml

BUILD_ROOT = "build"
JUNIT_FILENAME = "junit_tests_report.xml"
HTML_FILENAME = "tests_report.html"


def parse_build_root(project_yml_text):
    for line in project_yml_text.splitlines():
        stripped = line.strip()
        if stripped.startswith(":build_root:"):
            return stripped.split(":build_root:", 1)[1].strip().strip("'\"") or BUILD_ROOT
    return BUILD_ROOT


def parse_report_filename(project_yml_text, report_name, default_filename):
    in_report_factory = False
    in_report_block = False

    for line in project_yml_text.splitlines():
        stripped = line.strip()

        if not stripped:
            continue

        if not line.startswith(" "):
            in_report_factory = stripped == ":report_tests_log_factory:"
            in_report_block = False
            continue

        if not in_report_factory:
            continue

        if line.startswith("  :"):
            in_report_block = stripped == f":{report_name}:"
            continue

        if in_report_block and line.startswith("    :filename:"):
            return stripped.split(":filename:", 1)[1].strip().strip("'\"") or default_filename

    return default_filename


def parse_nested_list(project_yml_text, section_name, child_name):
    items = []
    in_section = False
    in_child = False

    for line in project_yml_text.splitlines():
        stripped = line.strip()

        if not stripped:
            continue

        if not line.startswith(" "):
            in_section = stripped == f":{section_name}:"
            in_child = False
            continue

        if not in_section:
            continue

        if line.startswith("  :"):
            in_child = stripped == f":{child_name}:"
            continue

        if in_child and line.startswith("    - "):
            items.append(stripped[2:].strip())

    return items


def validate_execute_configuration(project_yml_text, project_yml_path):
    enabled_plugins = parse_nested_list(project_yml_text, "plugins", "enabled")
    enabled_reports = parse_nested_list(project_yml_text, "report_tests_log_factory", "reports")
    build_root = parse_build_root(project_yml_text)
    junit_filename = parse_report_filename(project_yml_text, "junit", JUNIT_FILENAME)
    html_filename = parse_report_filename(project_yml_text, "html", HTML_FILENAME)

    issues = []

    if "report_tests_log_factory" not in enabled_plugins:
        issues.append("missing plugin ':plugins: :enabled: - report_tests_log_factory'")
    if "junit" not in enabled_reports:
        issues.append("missing report ':report_tests_log_factory: :reports: - junit'")
    if "html" not in enabled_reports:
        issues.append("missing report ':report_tests_log_factory: :reports: - html'")
    if build_root != BUILD_ROOT:
        issues.append(f"unsupported ':build_root:' value '{build_root}' (expected '{BUILD_ROOT}')")
    if junit_filename != JUNIT_FILENAME:
        issues.append(
            f"unsupported custom JUnit filename '{junit_filename}' (expected '{JUNIT_FILENAME}')"
        )
    if html_filename != HTML_FILENAME:
        issues.append(
            f"unsupported custom HTML filename '{html_filename}' (expected '{HTML_FILENAME}')"
        )

    if issues:
        raise ValueError(
            "project.yml is not compatible with Execute unit tests [ceedling]. "
            f"Issues: {', '.join(issues)}. File: {project_yml_path}. "
            "Re-run the init tool or restore the default Ceedling report settings."
        )


ceedling_command = get_setting(settings, "Ceedling command", "ceedling")

project_yml_path = os.path.join(taste_project_directory, "project.yml") if taste_project_directory else ""
ceedling_path = shutil.which(ceedling_command)

if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
elif ceedling_path is None:
    status = "error"
    status_text = f"{ceedling_command} not found in PATH"
elif not os.path.isfile(project_yml_path):
    status = "error"
    status_text = f"project.yml not found: {project_yml_path}"
else:
    try:
        with open(project_yml_path, "r", encoding="utf-8") as handle:
            project_yml_text = handle.read()

        validate_execute_configuration(project_yml_text, project_yml_path)

        status = "ok"
        status_text = (
            f"Ready to run Ceedling tests from {project_yml_path} and write reports to "
            f"{os.path.join(taste_project_directory, BUILD_ROOT, 'artifacts', 'test')}"
        )
    except Exception as exc:
        status = "error"
        status_text = str(exc)