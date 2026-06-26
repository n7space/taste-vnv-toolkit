import os
import shutil


ceedling_command = "ceedling"
for _name, _value in settings:
    if _name == "Ceedling command":
        ceedling_command = str(_value)

project_yml_path = os.path.join(taste_project_directory, "project.yml") if taste_project_directory else ""
ceedling_path = shutil.which(ceedling_command)

if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
elif ceedling_path is None:
    status = "error"
    status_text = f"{ceedling_command} not found in PATH"
elif not os.path.isfile(project_yml_path):
    status = "error"
    status_text = f"project.yml not found: {project_yml_path}"
else:
    status = "ok"
    status_text = f"Ready to run Ceedling tests from {project_yml_path}"