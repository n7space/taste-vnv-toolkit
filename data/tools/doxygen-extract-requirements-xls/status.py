"""Check status of requirements extraction tool."""

from vnvtoolkit import get_setting
import os


if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
    show_status = True
else:
    excel_file = str(get_setting(settings, "Excel file name", "demo_requirements.xlsx"))
    excel_path = os.path.join(taste_project_directory, excel_file)
    
    if not os.path.isfile(excel_path):
        status = "error"
        status_text = f"Excel file not found: {excel_path}\nConfigure the 'Excel file name' setting or place the file in the project directory."
        show_status = True
    else:
        # Check if openpyxl is available
        try:
            import openpyxl
            status = "ok"
            status_text = f"Ready to extract requirements from: {excel_path}"
            show_status = True
        except ImportError:
            status = "error"
            status_text = "openpyxl library is required but not installed.\nInstall with: pip install openpyxl"
            show_status = True
