import os

if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
    show_status = True
else:
    doxyfile_path = os.path.join(taste_project_directory, "Doxyfile")

    if not os.path.isfile(doxyfile_path):
        status = "error"
        status_text = f"Doxyfile not found: {doxyfile_path}\nRun the tool first to initialize it."
        show_status = True
    else:
        try:
            with open(doxyfile_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            status = "ok"
            status_text = content
            show_status = True
        except Exception as exc:
            status = "error"
            status_text = f"Failed to read Doxyfile: {exc}"
            show_status = True
