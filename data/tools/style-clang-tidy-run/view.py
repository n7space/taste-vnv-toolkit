import os

from vnvtoolkit import get_project_name, open_in_os_viewer, resolve_path

if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
    show_status = True
else:
    project_name = get_project_name(taste_project_directory)
    output_filename = f"{project_name}-code-naming-report.html"

    candidate_paths = []
    if output_directory:
        resolved_output = resolve_path(taste_project_directory, output_directory)
        candidate_paths.append(os.path.join(resolved_output, output_filename))

    candidate_paths.append(
        os.path.join(taste_project_directory, "output", output_filename)
    )

    report_path = next((path for path in candidate_paths if os.path.isfile(path)), "")

    if not report_path:
        status = "error"
        status_text = (
            "Code naming HTML report not found. Run the tool first to generate it."
        )
        show_status = True
    else:
        try:
            open_in_os_viewer(report_path)
            status = "ok"
            status_text = f"Opened code naming HTML report: {report_path}"
            show_status = False
        except Exception as exc:
            status = "error"
            status_text = f"Failed to open code naming HTML report: {exc}"
            show_status = True
