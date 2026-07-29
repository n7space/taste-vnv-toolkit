from doxygenshared import (
    get_doxygen_command,
    get_doxyfile_path,
    check_doxyfile_exists,
)

from vnvtoolkit import check_command_availability

if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
else:
    doxygen_command = get_doxygen_command(settings)
    doxygen_status, doxygen_message = check_command_availability(doxygen_command)

    if doxygen_status == "error":
        status = "error"
        status_text = doxygen_message
    else:
        doxyfile_path = get_doxyfile_path(taste_project_directory)
        exists, error_message = check_doxyfile_exists(doxyfile_path)

        if not exists:
            status = "error"
            status_text = error_message
        else:
            status = "ok"
            status_text = f"Ready to generate documentation using {doxyfile_path}"
