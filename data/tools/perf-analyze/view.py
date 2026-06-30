"""Display the generated performance analysis HTML report."""

import os
import subprocess
import sys


def get_setting(settings, name, default_value):
    """Get a setting value by name, or return default if not found."""
    for setting_name, setting_value in settings:
        if setting_name == name:
            return setting_value
    return default_value


def open_path(path):
    """Open a file or directory using the system default application."""
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
    # Derive project name from project directory
    project_name = os.path.basename(os.path.abspath(taste_project_directory))
    output_filename = f"{project_name}-performance-report.html"
    
    # Build candidate paths for the report
    candidate_paths = []
    if output_directory:
        # Resolve output_directory relative to project_directory
        if os.path.isabs(output_directory):
            resolved_output = output_directory
        else:
            resolved_output = os.path.join(taste_project_directory, output_directory)
        candidate_paths.append(os.path.join(resolved_output, output_filename))
    
    # Fallback to legacy output directory if configured
    candidate_paths.append(os.path.join(taste_project_directory, "output", output_filename))
    
    report_path = next((path for path in candidate_paths if os.path.isfile(path)), "")
    
    if not report_path:
        status = "error"
        status_text = "Performance analysis HTML report not found. Run the tool first to generate it."
        show_status = True
    else:
        try:
            open_path(report_path)
            status = "ok"
            status_text = f"Opened performance analysis HTML report: {report_path}"
            show_status = False
        except Exception as exc:
            status = "error"
            status_text = f"Failed to open performance analysis HTML report: {exc}"
            show_status = True
