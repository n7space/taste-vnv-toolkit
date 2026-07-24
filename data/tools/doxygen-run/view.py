from doxygenshared import (
    get_output_directory,
    get_documentation_paths,
)
from vnvtoolkit import open_in_os_viewer
import os

output_dir = get_output_directory(settings)

if not output_dir:
    status = "error"
    status_text = "Output directory is not configured"
    show_status = True
elif not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
    show_status = True
else:
    docs_path, html_path, index_path = get_documentation_paths(
        taste_project_directory, output_dir
    )

    if not os.path.isdir(html_path):
        status = "error"
        status_text = f"Documentation not found: {html_path}\nRun the tool first to generate it."
        show_status = True
    else:
        try:
            if os.path.isfile(index_path):
                open_in_os_viewer(index_path)
                status = "ok"
                status_text = f"Opened documentation: {index_path}"
            else:
                open_in_os_viewer(html_path)
                status = "ok"
                status_text = f"Opened documentation directory: {html_path}"
            show_status = False
        except Exception as exc:
            status = "error"
            status_text = f"Failed to open documentation: {exc}"
            show_status = True
