"""Display the generated Doxygen requirements tag file."""

from vnvtoolkit import get_setting
import os


if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
    show_status = True
else:
    output_tag_file = str(get_setting(settings, "Output tag file", "doxygen-requirements.tag"))
    tag_file_path = os.path.join(taste_project_directory, output_tag_file)
    
    if not os.path.isfile(tag_file_path):
        status = "error"
        status_text = f"Tag file not found: {tag_file_path}\nRun the tool first to extract requirements."
        show_status = True
    else:
        try:
            with open(tag_file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            status = "ok"
            status_text = content
            show_status = True
        except Exception as exc:
            status = "error"
            status_text = f"Failed to read tag file: {exc}"
            show_status = True
