import os
import shutil

from testsharedceedling import get_setting, parse_project_yml


def parse_build_root(project_yml_text):
    for line in project_yml_text.splitlines():
        stripped = line.strip()
        if stripped.startswith(":build_root:"):
            return stripped.split(":build_root:", 1)[1].strip().strip("'\"") or "build"
    return "build"


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
            return stripped.split(":html_artifact_filename:", 1)[1].strip().strip("'\"") or "GcovCoverageResults.html"

    return "GcovCoverageResults.html"


def validate_coverage_configuration(project_yml_text, project_yml_path):
    enabled_plugins = parse_nested_list(project_yml_text, "plugins", "enabled")

    issues = []

    if "gcov" not in enabled_plugins:
        issues.append("missing plugin ':plugins: :enabled: - gcov'")

    if issues:
        raise ValueError(
            "project.yml is not compatible with Gather unit test coverage [ceedling]. "
            f"Issues: {', '.join(issues)}. File: {project_yml_path}. "
            "Re-run the init tool or restore the default Ceedling gcov settings."
        )


ceedling_command = get_setting(settings, "Ceedling command", "ceedling")
html_filename = get_setting(settings, "HTML coverage report filename", "GcovCoverageResults.html")

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
        
        build_root = parse_build_root(project_yml_text)

        status = "ok"
        status_text = (
            f"Ready to gather Ceedling coverage from {project_yml_path} and write HTML output to "
            f"{os.path.join(taste_project_directory, build_root, 'artifacts', 'gcov', 'gcovr', html_filename)}"
        )
    except Exception as exc:
        status = "error"
        status_text = str(exc)