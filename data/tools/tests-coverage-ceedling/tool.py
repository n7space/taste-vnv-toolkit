import os
import shutil
import subprocess


BUILD_ROOT = "build"
GCOV_CONTEXT = os.path.join("gcov", "gcovr")
GCOV_HTML_FILENAME = "GcovCoverageResults.html"


def emit_progress(value):
    if "report_progress" in globals():
        report_progress(value)


def get_setting(name, default_value):
    for setting_name, setting_value in settings:
        if setting_name == name:
            return setting_value
    return default_value


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


def resolve_output_paths(project_directory):
    artifacts_directory = os.path.join(project_directory, BUILD_ROOT, "artifacts", GCOV_CONTEXT)
    html_source = os.path.join(artifacts_directory, GCOV_HTML_FILENAME)

    if output_directory:
        target_directory = os.path.join(output_directory, "ceedling-coverage-reports")
    else:
        target_directory = artifacts_directory

    html_target = os.path.join(target_directory, GCOV_HTML_FILENAME)
    return artifacts_directory, html_source, target_directory, html_target


def format_missing_report_error(expected_path, artifacts_directory, completed):
    command_output = ((completed.stdout or "") + (completed.stderr or "")).strip()
    artifact_summary = summarize_directory(artifacts_directory)
    message = (
        f"Coverage HTML report was not generated at the expected path: {expected_path}. "
        f"Checked artifacts directory: {artifacts_directory}. Contents: {artifact_summary}."
    )

    if command_output:
        message += f" Ceedling output: {command_output}"

    message += (
        " This tool expects the default gcovr HTML artifact name and output location produced by the init tool."
    )
    return message


ceedling_command = str(get_setting("Ceedling command", "ceedling"))
project_yml_path = os.path.join(taste_project_directory, "project.yml") if taste_project_directory else ""

if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
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

        artifacts_directory, html_source, target_directory, html_target = resolve_output_paths(
            taste_project_directory
        )

        if not os.path.isfile(html_source):
            raise FileNotFoundError(
                format_missing_report_error(html_source, artifacts_directory, completed)
            )

        if output_directory:
            os.makedirs(target_directory, exist_ok=True)
            shutil.copy2(html_source, html_target)
        else:
            html_target = html_source

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