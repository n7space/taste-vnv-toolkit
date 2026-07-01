from doxygenshared import (
    get_doxygen_command,
    get_output_directory,
    get_requirements_tag,
    create_doxyfile,
)
import os


def emit_progress(value):
    if "report_progress" in globals():
        report_progress(value)


doxygen_command = get_doxygen_command(settings)
requirements_tag = get_requirements_tag(settings)
output_dir = get_output_directory(settings)

if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
    show_status = True
else:
    try:
        emit_progress(10)
        
        doxyfile_path = os.path.join(taste_project_directory, "Doxyfile")
        
        # Create Doxyfile content
        doxyfile_content = create_doxyfile(
            taste_project_directory,
            output_dir,
            requirements_tag,
            doxygen_command
        )
        
        emit_progress(80)
        
        # Write Doxyfile
        with open(doxyfile_path, "w", encoding="utf-8") as f:
            f.write(doxyfile_content)
        
        emit_progress(100)
        
        status = "ok"
        status_text = f"Created Doxyfile at: {doxyfile_path}"
        show_status = True
        
    except Exception as exc:
        status = "error"
        status_text = f"Failed to create Doxyfile: {exc}"
        show_status = True
