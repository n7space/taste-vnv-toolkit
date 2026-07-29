from doxygenshared import get_doxygen_command
from vnvtoolkit import check_command_availability

doxygen_command = get_doxygen_command(settings)
status, status_text = check_command_availability(doxygen_command)
