"""
status.py – GCC Help tool status script

Sets:
  status      – "ok" if gcc is present, "error" otherwise
  status_text – human-readable explanation

Provided by the toolkit:
  tool_directory, taste_project_directory, intermediate_directory,
  output_directory, settings  (list of (name, value) tuples)
"""

import shutil

gcc_path = shutil.which("gcc")

if gcc_path is not None:
    status = "ok"
    status_text = f"gcc found at {gcc_path}"
else:
    status = "error"
    status_text = "gcc not found in PATH"
