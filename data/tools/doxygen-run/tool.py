from doxygenshared import (
    get_doxygen_command,
    get_output_directory,
    get_doxyfile_path,
    check_doxyfile_exists,
    get_documentation_paths,
)
import os
import subprocess


def emit_progress(value):
    if "report_progress" in globals():
        report_progress(value)


doxygen_command = get_doxygen_command(settings)
output_dir = get_output_directory(settings)

if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
    show_status = True
else:
    doxyfile_path = get_doxyfile_path(taste_project_directory)
    exists, error_message = check_doxyfile_exists(doxyfile_path)
    
    if not exists:
        status = "error"
        status_text = error_message
        show_status = True
    else:
        try:
            emit_progress(10)
            
            # Run doxygen
            completed = subprocess.run(
                [doxygen_command, doxyfile_path],
                cwd=taste_project_directory,
                capture_output=True,
                text=True,
                check=False,
            )
            
            emit_progress(80)
            
            if completed.returncode != 0:
                command_output = (completed.stdout or "") + (completed.stderr or "")
                raise RuntimeError(
                    f"Doxygen failed with exit code {completed.returncode}\n{command_output.strip()}"
                )
            
            # Get documentation paths
            docs_path, html_path, index_path = get_documentation_paths(
                taste_project_directory, output_dir
            )
            
            emit_progress(100)
            
            if os.path.isfile(index_path):
                status = "ok"
                status_text = f"Generated documentation at: {index_path}"
            else:
                status = "ok"
                status_text = f"Generated documentation in: {html_path}"
            show_status = True
            
        except Exception as exc:
            status = "error"
            status_text = f"Failed to generate documentation: {exc}"
            show_status = True
