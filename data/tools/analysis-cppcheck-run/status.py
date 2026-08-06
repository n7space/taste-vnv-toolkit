import os

from cppcheckshared import (
    get_cppcheck_command,
    get_misra_enabled,
    get_misra_rule_texts_path,
)
from vnvtoolkit import check_build_dir_present, check_command_availability

if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
else:
    cppcheck_command = get_cppcheck_command(settings)
    status, status_text = check_command_availability(cppcheck_command)

    if status == "ok":
        status, status_text = check_build_dir_present(taste_project_directory)
        if status == "ok":
            misra_rule_texts_path = get_misra_rule_texts_path(
                settings, taste_project_directory
            )
            if (
                get_misra_enabled(settings)
                and misra_rule_texts_path
                and not os.path.isfile(misra_rule_texts_path)
            ):
                status = "error"
                status_text = (
                    f"MISRA rule texts file not found: {misra_rule_texts_path}"
                )
            else:
                status_text = "Ready to generate static analysis report with Cppcheck"
