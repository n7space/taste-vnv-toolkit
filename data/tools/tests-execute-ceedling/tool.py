import os
import shutil
import subprocess

from testsharedceedling import (
    get_setting,
    parse_project_yml,
    emit_progress,
    resolve_test_output_paths,
    format_missing_test_report_error,
)


ceedling_command = str(get_setting(settings, "Ceedling command", "ceedling"))
junit_filename = str(get_setting(settings, "JUnit report filename", "junit_tests_report.xml"))
html_filename = str(get_setting(settings, "HTML report filename", "tests_report.html"))
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
        ) = resolve_test_output_paths(taste_project_directory, build_root, test_directory, output_directory, junit_filename, html_filename)

        if not os.path.isfile(junit_source):
            raise FileNotFoundError(
                format_missing_test_report_error("JUnit XML report", junit_source, artifacts_directory, completed)
            )
        if not os.path.isfile(html_source):
            raise FileNotFoundError(
                format_missing_test_report_error("HTML report", html_source, artifacts_directory, completed)
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