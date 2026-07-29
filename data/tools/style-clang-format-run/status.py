from clangshared import (
    check_clang_format_file_exists,
    get_clang_format_command,
    get_clang_format_file_path,
)
from vnvtoolkit import check_command_availability

if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
else:
    clang_command = get_clang_format_command(settings)
    status, status_text = check_command_availability(clang_command)

    if status == "ok":
        file_path = get_clang_format_file_path(taste_project_directory)
        exists, error_message = check_clang_format_file_exists(file_path)

        if not exists:
            status = "error"
            status_text = error_message
        else:
            status_text = (
                f"Ready to generate code style compliance report using {file_path}"
            )
