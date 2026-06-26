import os
import re
import subprocess
import sys


def get_setting(name, default_value):
    for setting_name, setting_value in settings:
        if setting_name == name:
            return setting_value
    return default_value


def parse_project_yml(project_yml_path):
    """Parse project.yml to extract build_root and test directory."""
    build_root = "build"
    test_directory = "test"
    
    if not os.path.isfile(project_yml_path):
        return build_root, test_directory
    
    try:
        with open(project_yml_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Extract :build_root: value
        build_root_match = re.search(r'^\s*:build_root:\s*(.+?)\s*$', content, re.MULTILINE)
        if build_root_match:
            build_root = build_root_match.group(1).strip()
        
        # Extract first :test: path (format: - +:test/** or - test/**)
        test_path_match = re.search(r'^\s*:test:\s*$\s*^\s*-\s*\+?:?(.+?)(?:/\*\*)?(?:\s|$)', content, re.MULTILINE)
        if test_path_match:
            test_directory = test_path_match.group(1).strip()
    
    except Exception:
        # If parsing fails, use defaults
        pass
    
    return build_root, test_directory


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


html_filename = str(get_setting("HTML report filename", "tests_report.html"))
project_yml_path = os.path.join(taste_project_directory, "project.yml") if taste_project_directory else ""

if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
    show_status = True
else:
    build_root, test_directory = parse_project_yml(project_yml_path)
    
    candidate_paths = []
    if output_directory:
        # Resolve output_directory relative to project_directory
        if os.path.isabs(output_directory):
            resolved_output = output_directory
        else:
            resolved_output = os.path.join(taste_project_directory, output_directory)
        candidate_paths.append(os.path.join(resolved_output, "ceedling-test-reports", html_filename))
    candidate_paths.append(
        os.path.join(taste_project_directory, build_root, "artifacts", test_directory, html_filename)
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