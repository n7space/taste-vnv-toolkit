import os
import shutil


BUILD_ROOT = "build"
GCOV_HTML_FILENAME = "GcovCoverageResults.html"


def parse_build_root(project_yml_text):
    for line in project_yml_text.splitlines():
        stripped = line.strip()
        if stripped.startswith(":build_root:"):
            return stripped.split(":build_root:", 1)[1].strip().strip("'\"") or BUILD_ROOT
    return BUILD_ROOT


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


def parse_gcov_html_filename(project_yml_text):
    in_gcov = False
    in_gcovr = False

    for line in project_yml_text.splitlines():
        stripped = line.strip()

        if not stripped:
            continue

        if not line.startswith(" "):
            in_gcov = stripped == ":gcov:"
            in_gcovr = False
            continue

        if not in_gcov:
            continue

        if line.startswith("  :"):
            in_gcovr = stripped == ":gcovr:"
            continue

        if in_gcovr and line.startswith("    :html_artifact_filename:"):
            return stripped.split(":html_artifact_filename:", 1)[1].strip().strip("'\"") or GCOV_HTML_FILENAME

    return GCOV_HTML_FILENAME


def validate_coverage_configuration(project_yml_text, project_yml_path):
    enabled_plugins = parse_nested_list(project_yml_text, "plugins", "enabled")
    gcov_reports = parse_nested_list(project_yml_text, "gcov", "reports")
    gcov_utilities = parse_nested_list(project_yml_text, "gcov", "utilities")
    build_root = parse_build_root(project_yml_text)
    html_filename = parse_gcov_html_filename(project_yml_text)

    issues = []

    if "gcov" not in enabled_plugins:
        issues.append("missing plugin ':plugins: :enabled: - gcov'")
    if "HtmlBasic" not in gcov_reports:
        issues.append("missing report ':gcov: :reports: - HtmlBasic'")
    if gcov_utilities and "gcovr" not in gcov_utilities:
        issues.append("unsupported ':gcov: :utilities:' configuration without 'gcovr'")
    if build_root != BUILD_ROOT:
        issues.append(f"unsupported ':build_root:' value '{build_root}' (expected '{BUILD_ROOT}')")
    if html_filename != GCOV_HTML_FILENAME:
        issues.append(
            f"unsupported custom coverage HTML filename '{html_filename}' (expected '{GCOV_HTML_FILENAME}')"
        )

    if issues:
        raise ValueError(
            "project.yml is not compatible with Gather unit test coverage [ceedling]. "
            f"Issues: {', '.join(issues)}. File: {project_yml_path}. "
            "Re-run the init tool or restore the default Ceedling gcov settings."
        )


ceedling_command = "ceedling"
for _name, _value in settings:
    if _name == "Ceedling command":
        ceedling_command = str(_value)

project_yml_path = os.path.join(taste_project_directory, "project.yml") if taste_project_directory else ""
ceedling_path = shutil.which(ceedling_command)
gcovr_path = shutil.which("gcovr")

if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
elif ceedling_path is None:
    status = "error"
    status_text = f"{ceedling_command} not found in PATH"
elif gcovr_path is None:
    status = "error"
    status_text = "gcovr not found in PATH"
elif not os.path.isfile(project_yml_path):
    status = "error"
    status_text = f"project.yml not found: {project_yml_path}"
else:
    try:
        with open(project_yml_path, "r", encoding="utf-8") as handle:
            project_yml_text = handle.read()

        validate_coverage_configuration(project_yml_text, project_yml_path)

        status = "ok"
        status_text = (
            f"Ready to gather Ceedling coverage from {project_yml_path} and write HTML output to "
            f"{os.path.join(taste_project_directory, BUILD_ROOT, 'artifacts', 'gcov', 'gcovr', GCOV_HTML_FILENAME)}"
        )
    except Exception as exc:
        status = "error"
        status_text = str(exc)