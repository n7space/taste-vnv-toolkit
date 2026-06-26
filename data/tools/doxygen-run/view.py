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


def open_html_file(file_path):
    if sys.platform.startswith("win"):
        os.startfile(file_path)
        return

    command = ["open", file_path] if sys.platform == "darwin" else ["xdg-open", file_path]
    subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


# ── resolve settings ──────────────────────────────────────────────────────────

output_dir = "docs"
for _name, _value in settings:
    if _name == "Output directory":
        output_dir = str(_value)

# ── validate output directory ─────────────────────────────────────────────────

if not output_dir:
    status = "error"
    status_text = "Output directory is not configured"
    show_status = True
elif not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
    show_status = True
else:
    # Handle both absolute and relative paths
    if os.path.isabs(output_dir):
        docs_path = output_dir
    else:
        docs_path = os.path.join(taste_project_directory, output_dir)
    
    html_path = os.path.join(docs_path, "html")
    index_path = os.path.join(html_path, "index.html")

    if not os.path.isdir(html_path):
        status = "error"
        status_text = f"Documentation not found: {html_path}\nRun the tool first to generate it."
        show_status = True
    else:
        try:
            if os.path.isfile(index_path):
                open_html_file(index_path)
                status = "ok"
                status_text = f"Opened documentation: {index_path}"
            else:
                open_directory(html_path)
                status = "ok"
                status_text = f"Opened documentation directory: {html_path}"
            show_status = False
        except Exception as exc:
            status = "error"
            status_text = f"Failed to open documentation: {exc}"
            show_status = True
