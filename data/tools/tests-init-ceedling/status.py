from testsharedceedling import get_ceedling_command, check_ceedling_available

ceedling_command = get_ceedling_command(settings)
status, status_text = check_ceedling_available(ceedling_command)
