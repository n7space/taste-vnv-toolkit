import os
import subprocess
import sys


def open_directory(directory_path):
    if sys.platform.startswith("win"):
        os.startfile(directory_path)
        return

    command = ["open", directory_path] if sys.platform == "darwin" else ["xdg-open", directory_path]
    subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

# ── resolve settings ──────────────────────────────────────────────────────────

tests_folder = "test"
for _name, _value in settings:
    if _name == "Tests folder":
        tests_folder = str(_value)

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
