"""Check status of Performance Analysis tool."""

import os


def get_setting(settings, name, default_value):
    """Get a setting value by name, or return default if not found."""
    for setting_name, setting_value in settings:
        if setting_name == name:
            return setting_value
    return default_value


if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
    show_status = True
else:
    miab_file = str(get_setting(settings, "MIAB file path", "trace.miab"))
    interfaces_file = str(get_setting(settings, "interfaces_info.h path", 
                                      "work/build/node_1/samv71asw/interfaces_info.h"))
    
    # Build absolute paths
    if os.path.isabs(miab_file):
        miab_path = miab_file
    else:
        miab_path = os.path.join(taste_project_directory, miab_file)
    
    if os.path.isabs(interfaces_file):
        interfaces_path = interfaces_file
    else:
        interfaces_path = os.path.join(taste_project_directory, interfaces_file)
    
    # Check if files exist
    miab_exists = os.path.isfile(miab_path)
    interfaces_exists = os.path.isfile(interfaces_path)
    
    if not miab_exists and not interfaces_exists:
        status = "error"
        status_text = f"Required files not found:\n- MIAB file: {miab_path}\n- Interfaces file: {interfaces_path}"
        show_status = True
    elif not miab_exists:
        status = "error"
        status_text = f"MIAB file not found: {miab_path}\nPlease configure the correct path in settings."
        show_status = True
    elif not interfaces_exists:
        status = "error"
        status_text = f"Interfaces file not found: {interfaces_path}\nPlease configure the correct path in settings or build the project first."
        show_status = True
    else:
        status = "ok"
        status_text = f"Ready to analyze performance\n- MIAB file: {miab_path}\n- Interfaces file: {interfaces_path}"
        show_status = True
