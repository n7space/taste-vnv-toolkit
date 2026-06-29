from doxygenshared import get_doxyfile_path, check_doxyfile_exists

if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
    show_status = True
else:
    doxyfile_path = get_doxyfile_path(taste_project_directory)
    exists, error_message = check_doxyfile_exists(doxyfile_path)

    if not exists:
        status = "error"
        status_text = f"{error_message}\nRun the tool first to initialize it."
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
