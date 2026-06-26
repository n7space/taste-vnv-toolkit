import os
import shutil
import subprocess


JUNIT_FILENAME = "junit_tests_report.xml"
HTML_FILENAME = "tests_report.html"


def emit_progress(value):
    if "report_progress" in globals():
        report_progress(value)


def get_setting(name, default_value):
    for setting_name, setting_value in settings:
        if setting_name == name:
            return setting_value
    return default_value


def parse_build_root(project_yml_text):
    for line in project_yml_text.splitlines():
        stripped = line.strip()
        if stripped.startswith(":build_root:"):
            return stripped.split(":build_root:", 1)[1].strip().strip("'\"") or "build"
    return "build"


def parse_report_filename(project_yml_text, report_name, default_filename):
    lines = project_yml_text.splitlines()
    in_report_factory = False
    in_report_block = False

    for line in lines:
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


def parse_enabled_plugins(project_yml_text):
    plugins = []
    in_plugins = False
    in_enabled = False

    for line in project_yml_text.splitlines():
        stripped = line.strip()

        if not stripped:
            continue

        if not line.startswith(" "):
            in_plugins = stripped == ":plugins:"
            in_enabled = False
            continue

        if not in_plugins:
            continue

        if line.startswith("  :"):
            in_enabled = stripped == ":enabled:"
            continue

        if in_enabled and line.startswith("    - "):
            plugins.append(stripped[2:].strip())

    return plugins


def parse_enabled_reports(project_yml_text):
    reports = []
    in_report_factory = False
    in_reports = False

    for line in project_yml_text.splitlines():
        stripped = line.strip()

        if not stripped:
            continue

        if not line.startswith(" "):
            in_report_factory = stripped == ":report_tests_log_factory:"
            in_reports = False
            continue

        if not in_report_factory:
            continue

        if line.startswith("  :"):
            in_reports = stripped == ":reports:"
            continue

        if in_reports and line.startswith("    - "):
            reports.append(stripped[2:].strip())

    return reports


def validate_report_configuration(project_yml_text, project_yml_path):
    enabled_plugins = parse_enabled_plugins(project_yml_text)
    enabled_reports = parse_enabled_reports(project_yml_text)
    missing_items = []

    if "report_tests_log_factory" not in enabled_plugins:
        missing_items.append("plugin ':plugins: :enabled: - report_tests_log_factory'")
    if "junit" not in enabled_reports:
        missing_items.append("report ':report_tests_log_factory: :reports: - junit'")
    if "html" not in enabled_reports:
        missing_items.append("report ':report_tests_log_factory: :reports: - html'")

    if missing_items:
        raise ValueError(
            "Ceedling report configuration is missing from project.yml. "
            f"Missing: {', '.join(missing_items)}. "
            f"File: {project_yml_path}. "
            "The file exists, but it does not enable the reports required by this tool. "
            "This usually means project.yml was created before the init tool added report settings. "
            "Re-run the init tool or update project.yml to enable report_tests_log_factory with junit and html reports."
        )


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


def build_artifacts_directory(project_directory, build_root):
    return os.path.join(project_directory, build_root, "artifacts", "test")


def resolve_output_paths(project_directory, build_root, junit_filename, html_filename):
    artifacts_directory = build_artifacts_directory(project_directory, build_root)

    junit_source = os.path.join(artifacts_directory, junit_filename)
    html_source = os.path.join(artifacts_directory, html_filename)

    if output_directory:
        target_directory = os.path.join(output_directory, "ceedling-test-reports")
    else:
        target_directory = artifacts_directory

    junit_target = os.path.join(target_directory, junit_filename)
    html_target = os.path.join(target_directory, html_filename)
    return artifacts_directory, junit_source, html_source, target_directory, junit_target, html_target


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

        with open(project_yml_path, "r", encoding="utf-8") as handle:
            project_yml_text = handle.read()

        validate_report_configuration(project_yml_text, project_yml_path)

        build_root = parse_build_root(project_yml_text)
        junit_filename = parse_report_filename(project_yml_text, "junit", JUNIT_FILENAME)
        html_filename = parse_report_filename(project_yml_text, "html", HTML_FILENAME)

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
        ) = resolve_output_paths(taste_project_directory, build_root, junit_filename, html_filename)

        if not os.path.isfile(junit_source):
            raise FileNotFoundError(
                format_missing_report_error("JUnit XML report", junit_source, artifacts_directory, completed)
            )
        if not os.path.isfile(html_source):
            raise FileNotFoundError(
                format_missing_report_error("HTML report", html_source, artifacts_directory, completed)
            )

        if output_directory:
            os.makedirs(target_directory, exist_ok=True)
            shutil.copy2(junit_source, junit_target)
            shutil.copy2(html_source, html_target)
        else:
            junit_target = junit_source
            html_target = html_source

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