"""Display the generated TASTE stack usage HTML report."""

import os

from vnvtoolkit import get_setting, open_in_os_viewer, resolve_path


if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
    show_status = True
else:
    report_filename = str(get_setting(settings, "Report filename", "stack-usage-report.html"))
    
    # Build candidate paths for the report
    candidate_paths = []
    if output_directory:
        # Resolve output_directory relative to project_directory
        resolved_output = resolve_path(taste_project_directory, output_directory)
        candidate_paths.append(os.path.join(resolved_output, report_filename))
    
    # Fallback to legacy output directory if configured
    candidate_paths.append(os.path.join(taste_project_directory, "output", report_filename))
    
    report_path = next((path for path in candidate_paths if os.path.isfile(path)), "")
    
    if not report_path:
        status = "error"
        status_text = "Stack usage HTML report not found. Run the tool first to generate it."
        show_status = True
    else:
        try:
            open_in_os_viewer(report_path)
            status = "ok"
            status_text = f"Opened stack usage HTML report: {report_path}"
            show_status = False
        except Exception as exc:
            status = "error"
            status_text = f"Failed to open stack usage HTML report: {exc}"
            show_status = True
