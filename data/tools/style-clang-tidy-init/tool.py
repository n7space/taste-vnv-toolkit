import subprocess

from clangshared import get_clang_tidy_command, get_clang_style_file_path
from vnvtoolkit import get_setting


def emit_progress(value):
    if "report_progress" in globals():
        report_progress(value)

__DEFAULT_STYLE = """
Checks: '-*,readability-identifier-naming'

CheckOptions:
  - key: readability-identifier-naming.ClassCase
    value: CamelCase

  - key: readability-identifier-naming.FunctionCase
    value: camelBack

  - key: readability-identifier-naming.VariableCase
    value: lower_case

  - key: readability-identifier-naming.PrivateMemberPrefix
    value: m_
"""


if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
    show_status = True
else:
    try:
        emit_progress(10)

        file_path = get_clang_style_file_path(taste_project_directory)

        emit_progress(80)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(__DEFAULT_STYLE)

        emit_progress(100)

        status = "ok"
        status_text = f"Created .clang-tidy.style at: {file_path}"
        show_status = True

    except Exception as exc:
        status = "error"
        status_text = f"Failed to create .clang-tidy.style: {exc}"
        show_status = True
