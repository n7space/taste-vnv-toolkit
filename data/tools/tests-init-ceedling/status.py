import shutil

ceedling_command = "ceedling"
for _name, _value in settings:
    if _name == "Ceedling command":
        ceedling_command = str(_value)

path = shutil.which(ceedling_command)

if path is not None:
    status = "ok"
    status_text = f"{ceedling_command} found at {path}"
else:
    status = "error"
    status_text = f"{ceedling_command} not found in PATH"
