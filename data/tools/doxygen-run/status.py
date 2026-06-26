import os
import shutil

doxygen_command = "doxygen"
for _name, _value in settings:
    if _name == "Doxygen command":
        doxygen_command = str(_value)

doxygen_path = shutil.which(doxygen_command)
project_yml_path = os.path.join(taste_project_directory, "Doxyfile") if taste_project_directory else ""

if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
elif doxygen_path is None:
    status = "error"
    status_text = f"{doxygen_command} not found in PATH"
elif not os.path.isfile(project_yml_path):
    status = "error"
    status_text = f"Doxyfile not found: {project_yml_path}\nRun the 'Initialize Doxygen configuration' tool first."
else:
    status = "ok"
    status_text = f"Ready to generate documentation using {project_yml_path}"
