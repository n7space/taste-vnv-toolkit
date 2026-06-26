import os
import subprocess


def emit_progress(value):
    if "report_progress" in globals():
        report_progress(value)


def get_setting(name, default_value):
    for setting_name, setting_value in settings:
        if setting_name == name:
            return setting_value
    return default_value


doxygen_command = str(get_setting("Doxygen command", "doxygen"))
output_dir = str(get_setting("Output directory", "docs"))

if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
    show_status = True
else:
    doxyfile_path = os.path.join(taste_project_directory, "Doxyfile")
    
    if not os.path.isfile(doxyfile_path):
        status = "error"
        status_text = f"Doxyfile not found: {doxyfile_path}\nRun the 'Initialize Doxygen configuration' tool first."
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
            
            # Determine output path
            if os.path.isabs(output_dir):
                docs_path = output_dir
            else:
                docs_path = os.path.join(taste_project_directory, output_dir)
            
            html_path = os.path.join(docs_path, "html")
            index_path = os.path.join(html_path, "index.html")
            
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
