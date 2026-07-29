import os

from vnvtoolkit import get_setting, open_in_os_viewer, resolve_path
from testsharedceedling import parse_project_yml


html_filename = str(get_setting(settings, "HTML coverage report filename", "GcovCoverageResults.html"))
project_yml_path = os.path.join(taste_project_directory, "project.yml") if taste_project_directory else ""

if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
    show_status = True
else:
    build_root, test_directory = parse_project_yml(project_yml_path)
    gcov_context = os.path.join("gcov", "gcovr")
    
    candidate_paths = []
    if output_directory:
        # Resolve output_directory relative to project_directory
        resolved_output = resolve_path(taste_project_directory, output_directory)
        candidate_paths.append(
            os.path.join(resolved_output, "ceedling-coverage-reports", html_filename)
        )
    candidate_paths.append(
        os.path.join(taste_project_directory, build_root, "artifacts", gcov_context, html_filename)
    )

    report_path = next((path for path in candidate_paths if os.path.isfile(path)), "")

    if not report_path:
        status = "error"
        status_text = "Coverage HTML report not found. Run the tool first to generate it."
        show_status = True
    else:
        try:
            open_in_os_viewer(report_path)
            status = "ok"
            status_text = f"Opened coverage HTML report: {report_path}"
            show_status = False
        except Exception as exc:
            status = "error"
            status_text = f"Failed to open coverage HTML report: {exc}"
            show_status = True