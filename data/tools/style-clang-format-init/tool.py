import subprocess

from clangshared import get_clang_format_command, get_clang_format_file_path
from vnvtoolkit import get_setting


def emit_progress(value):
    if "report_progress" in globals():
        report_progress(value)


format_command = get_clang_format_command(settings)
style = get_setting(settings, "Base style", "GNU")

if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
    show_status = True
else:
    try:
        emit_progress(10)

        file_path = get_clang_format_file_path(taste_project_directory)

        content = subprocess.check_output(
            [
                format_command,
                f"--style={style}",
                "--dump-config",
            ],
            encoding="utf-8",
        )

        emit_progress(80)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        emit_progress(100)

        status = "ok"
        status_text = f"Created .clang-format at: {file_path}"
        show_status = True

    except Exception as exc:
        status = "error"
        status_text = f"Failed to create .clang-format: {exc}"
        show_status = True
