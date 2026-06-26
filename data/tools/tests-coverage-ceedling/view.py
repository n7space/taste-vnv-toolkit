import os
import subprocess
import sys


BUILD_ROOT = "build"
GCOV_CONTEXT = os.path.join("gcov", "gcovr")
GCOV_HTML_FILENAME = "GcovCoverageResults.html"


def open_path(path):
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
    candidate_paths = []
    if output_directory:
        candidate_paths.append(
            os.path.join(output_directory, "ceedling-coverage-reports", GCOV_HTML_FILENAME)
        )
    candidate_paths.append(
        os.path.join(taste_project_directory, BUILD_ROOT, "artifacts", GCOV_CONTEXT, GCOV_HTML_FILENAME)
    )

    report_path = next((path for path in candidate_paths if os.path.isfile(path)), "")

    if not report_path:
        status = "error"
        status_text = "Coverage HTML report not found. Run the tool first to generate it."
        show_status = True
    else:
        try:
            open_path(report_path)
            status = "ok"
            status_text = f"Opened coverage HTML report: {report_path}"
            show_status = False
        except Exception as exc:
            status = "error"
            status_text = f"Failed to open coverage HTML report: {exc}"
            show_status = True