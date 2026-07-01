import os

from testsharedceedling import get_setting, open_directory


# ── resolve settings ──────────────────────────────────────────────────────────

tests_folder = str(get_setting(settings, "Tests folder", "test"))

# ── validate output directory ─────────────────────────────────────────────────

if not tests_folder:
    status = "error"
    status_text = "Test folder is not configured"
    show_status = True
elif not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
    show_status = True
else:
    tests_path = os.path.abspath(os.path.join(taste_project_directory, tests_folder))

    if not os.path.isdir(tests_path):
        status = "error"
        status_text = f"Tests directory not found: {tests_path}\nRun the tool first to initialize it."
        show_status = True
    else:
        try:
            open_directory(tests_path)
            status = "ok"
            status_text = f"Opened tests directory: {tests_path}"
            show_status = False
        except Exception as _exc:
            status = "error"
            status_text = f"Failed to open tests directory: {_exc}"
            show_status = True
