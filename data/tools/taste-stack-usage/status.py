"""Check status of TASTE stack usage analyzer."""

import os
import shutil


if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
    show_status = True
else:
    work_dir = os.path.join(taste_project_directory, "work")
    
    if not os.path.isdir(work_dir):
        status = "error"
        status_text = f"Work directory not found: {work_dir}\nMake sure the TASTE project is properly configured."
        show_status = True
    else:
        # Check if make is available
        make_path = shutil.which("make")
        if not make_path:
            status = "error"
            status_text = "make command not found in PATH"
            show_status = True
        else:
            status = "ok"
            status_text = f"Ready to analyze stack usage\nWork directory: {work_dir}\nmake found at: {make_path}"
            show_status = True
