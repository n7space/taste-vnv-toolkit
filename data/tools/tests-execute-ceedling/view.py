import os

from testsharedceedling import get_setting, parse_project_yml, open_path


html_filename = str(get_setting(settings, "HTML report filename", "tests_report.html"))
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