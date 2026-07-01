import os
import shutil
import subprocess

from testsharedceedling import (
    get_setting,
    parse_project_yml,
    emit_progress,
    resolve_coverage_output_paths,
    format_missing_coverage_report_error,
)


ceedling_command = str(get_setting(settings, "Ceedling command", "ceedling"))
html_filename = str(get_setting(settings, "HTML coverage report filename", "GcovCoverageResults.html"))
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
            [ceedling_command, "gcov:all"],
            cwd=taste_project_directory,
            capture_output=True,
            text=True,
            check=False,
        )

        emit_progress(75)

        if completed.returncode != 0:
            command_output = (completed.stdout or "") + (completed.stderr or "")
            raise RuntimeError(
                f"Ceedling coverage run failed with exit code {completed.returncode}\n{command_output.strip()}"
            )

        artifacts_directory, html_source, target_directory, html_target = resolve_coverage_output_paths(
            taste_project_directory, build_root, test_directory, output_directory, html_filename
        )

        if not os.path.isfile(html_source):
            raise FileNotFoundError(
                format_missing_coverage_report_error(html_source, artifacts_directory, completed)
            )

        os.makedirs(target_directory, exist_ok=True)
        
        # Copy all files from artifacts directory to preserve CSS, supporting HTML files, etc.
        if os.path.isdir(artifacts_directory):
            for item in os.listdir(artifacts_directory):
                source_item = os.path.join(artifacts_directory, item)
                target_item = os.path.join(target_directory, item)
                if os.path.isfile(source_item):
                    shutil.copy2(source_item, target_item)

        emit_progress(100)

        status = "ok"
        status_text = f"Generated Ceedling coverage HTML report: {html_target}"
        show_status = True

    except FileNotFoundError as exc:
        status = "error"
        status_text = str(exc)
        show_status = True

    except Exception as exc:
        status = "error"
        status_text = f"Unexpected error: {exc}"
        show_status = True