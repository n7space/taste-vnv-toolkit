from clangshared import get_clang_tidy_command
from vnvtoolkit import check_command_availability

clang_command = get_clang_tidy_command(settings)
status, status_text = check_command_availability(clang_command)
