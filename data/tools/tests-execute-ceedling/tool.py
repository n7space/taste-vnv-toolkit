import os
import re
import shutil
import subprocess


def emit_progress(value):
    if "report_progress" in globals():
        report_progress(value)


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


def summarize_directory(directory_path):
    if not os.path.isdir(directory_path):
        return "directory does not exist"

    entries = sorted(os.listdir(directory_path))
    if not entries:
        return "directory is empty"

    preview = ", ".join(entries[:10])
    if len(entries) > 10:
        preview += f", ... ({len(entries)} entries total)"
    return preview


def format_missing_report_error(report_label, expected_path, artifacts_directory, completed):
    command_output = ((completed.stdout or "") + (completed.stderr or "")).strip()
    artifact_summary = summarize_directory(artifacts_directory)
    message = (
        f"{report_label} was not generated at the expected path: {expected_path}. "
        f"Checked artifacts directory: {artifacts_directory}. Contents: {artifact_summary}."
    )

    if command_output:
        message += f" Ceedling output: {command_output}"

    message += (
        " If project.yml enables report_tests_log_factory with the expected report, "
        "this may indicate Ceedling wrote the report under a different filename or context."
    )
    return message


def build_artifacts_directory(project_directory, build_root, test_directory):
    return os.path.join(project_directory, build_root, "artifacts", test_directory)


def resolve_output_paths(project_directory, build_root, test_directory, junit_filename, html_filename):
    artifacts_directory = build_artifacts_directory(project_directory, build_root, test_directory)

    junit_source = os.path.join(artifacts_directory, junit_filename)
    html_source = os.path.join(artifacts_directory, html_filename)

    if not output_directory:
        raise ValueError("Output directory is not configured")
    
    # Resolve output_directory relative to project_directory
    if os.path.isabs(output_directory):
        resolved_output = output_directory
    else:
        resolved_output = os.path.join(project_directory, output_directory)
    
    target_directory = os.path.join(resolved_output, "ceedling-test-reports")
    junit_target = os.path.join(target_directory, junit_filename)
    html_target = os.path.join(target_directory, html_filename)
    
    return artifacts_directory, junit_source, html_source, target_directory, junit_target, html_target


ceedling_command = str(get_setting("Ceedling command", "ceedling"))
junit_filename = str(get_setting("JUnit report filename", "junit_tests_report.xml"))
html_filename = str(get_setting("HTML report filename", "tests_report.html"))
project_yml_path = os.path.join(taste_project_directory, "project.yml") if taste_project_directory else ""

if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
    show_status = True
elif not output_directory:
    status = "error"
    status_text = "Output directory is not configured"
    show_status = True
elif shutil.which(ceedling_command) is None:
    status = "error"
    status_text = f"{ceedling_command} not found in PATH"
    show_status = True
elif not os.path.isfile(project_yml_path):
    status = "error"
    status_text = f"project.yml not found: {project_yml_path}"
    show_status = True
else:
    try:
        emit_progress(5)
        
        # Parse project.yml to get build_root and test directory
        build_root, test_directory = parse_project_yml(project_yml_path)
        
        emit_progress(20)

        completed = subprocess.run(
            [ceedling_command, "test:all"],
            cwd=taste_project_directory,
            capture_output=True,
            text=True,
            check=False,
        )

        emit_progress(75)

        if completed.returncode != 0:
            command_output = (completed.stdout or "") + (completed.stderr or "")
            raise RuntimeError(
                f"Ceedling test run failed with exit code {completed.returncode}\n{command_output.strip()}"
            )

        (
            artifacts_directory,
            junit_source,
            html_source,
            target_directory,
            junit_target,
            html_target,
        ) = resolve_output_paths(taste_project_directory, build_root, test_directory, junit_filename, html_filename)

        if not os.path.isfile(junit_source):
            raise FileNotFoundError(
                format_missing_report_error("JUnit XML report", junit_source, artifacts_directory, completed)
            )
        if not os.path.isfile(html_source):
            raise FileNotFoundError(
                format_missing_report_error("HTML report", html_source, artifacts_directory, completed)
            )

        os.makedirs(target_directory, exist_ok=True)
        shutil.copy2(junit_source, junit_target)
        shutil.copy2(html_source, html_target)

        emit_progress(100)

        status = "ok"
        status_text = (
            "Executed Ceedling unit tests successfully. "
            f"JUnit XML: {junit_target}; HTML: {html_target}"
        )
        show_status = True

    except FileNotFoundError as exc:
        status = "error"
        status_text = str(exc)
        show_status = True

    except Exception as exc:
        status = "error"
        status_text = f"Unexpected error: {exc}"
        show_status = True