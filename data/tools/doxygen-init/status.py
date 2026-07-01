from doxygenshared import get_doxygen_command, check_doxygen_available

doxygen_command = get_doxygen_command(settings)
status, status_text = check_doxygen_available(doxygen_command)
