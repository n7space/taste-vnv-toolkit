import os
import re
import subprocess
import sys


HTML_FILENAME = "tests_report.html"


def parse_build_root(project_yml_path):
    if not os.path.isfile(project_yml_path):
        return "build"

    with open(project_yml_path, "r", encoding="utf-8") as handle:
        project_yml_text = handle.read()

    match = re.search(r"(?m)^\s*:build_root:\s*(\S+)\s*$", project_yml_text)
    if match:
        return match.group(1).strip().strip("'\"")
    return "build"


def parse_html_filename(project_yml_path):
    if not os.path.isfile(project_yml_path):
        return HTML_FILENAME

    with open(project_yml_path, "r", encoding="utf-8") as handle:
        project_yml_text = handle.read()

    match = re.search(
        r"(?ms)^:report_tests_log_factory:.*?^\s*:html:\s*$.*?^\s*:filename:\s*['\"]?([^'\"\n]+)['\"]?\s*$",
        project_yml_text,
    )
    if match:
        return match.group(1).strip()

    return HTML_FILENAME


def open_path(path):
    if sys.platform.startswith("win"):
        os.startfile(path)
        return

    command = ["open", path] if sys.platform == "darwin" else ["xdg-open", path]
    subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
    show_status = True
else:
    project_yml_path = os.path.join(taste_project_directory, "project.yml")
    build_root = parse_build_root(project_yml_path)
    html_filename = parse_html_filename(project_yml_path)

    candidate_paths = []
    if output_directory:
        candidate_paths.append(os.path.join(output_directory, "ceedling-test-reports", html_filename))
    candidate_paths.append(
        os.path.join(taste_project_directory, build_root, "artifacts", "test", html_filename)
    )

    report_path = next((path for path in candidate_paths if os.path.isfile(path)), "")

    if not report_path:
        status = "error"
        status_text = "HTML report not found. Run the tool first to generate it."
        show_status = True
    else:
        try:
            open_path(report_path)
            status = "ok"
            status_text = f"Opened HTML report: {report_path}"
            show_status = False
        except Exception as exc:
            status = "error"
            status_text = f"Failed to open HTML report: {exc}"
            show_status = True