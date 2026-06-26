import shutil

doxygen_command = "doxygen"
for _name, _value in settings:
    if _name == "Doxygen command":
        doxygen_command = str(_value)

path = shutil.which(doxygen_command)

if path is not None:
    status = "ok"
    status_text = f"{doxygen_command} found at {path}"
else:
    status = "error"
    status_text = f"{doxygen_command} not found in PATH"
