"""
view.py – GCC Help tool view script

Shows the previously saved gcc --help output file in a Tk dialog.
Returns an error (show_status = True) if the file does not exist yet.

Sets:
  status      – "ok" / "error"
  status_text – human-readable result
  show_status – True on error, False when the dialog handles display

Provided by the toolkit:
  tool_directory, taste_project_directory, intermediate_directory,
  output_directory, settings  (list of (name, value) tuples)
"""

import os

# ── resolve settings ──────────────────────────────────────────────────────────

output_filename = "gcc_help.txt"
for _name, _value in settings:
    if _name == "output_filename":
        output_filename = str(_value)

# ── validate output directory ─────────────────────────────────────────────────

if not output_directory:
    status = "error"
    status_text = "Output directory is not configured"
    show_status = True
else:
    output_path = os.path.join(output_directory, output_filename)

    if not os.path.isfile(output_path):
        status = "error"
        status_text = f"Output file not found: {output_path}\nRun the tool first to generate it."
        show_status = True
    else:
        with open(output_path, "r", encoding="utf-8") as fh:
            content = fh.read()

        status = "ok"
        status_text = "Results displayed"
        show_status = False

        try:
            import tkinter as tk
            from tkinter import scrolledtext

            root = tk.Tk()
            root.title(f"gcc --help  –  {output_path}")
            root.geometry("720x520")

            txt = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Monospace", 10))
            txt.pack(expand=True, fill=tk.BOTH, padx=8, pady=8)
            txt.insert(tk.END, content)
            txt.config(state=tk.DISABLED)

            btn = tk.Button(root, text="Close", width=12, command=root.destroy)
            btn.pack(pady=(0, 8))

            root.mainloop()

        except ImportError:
            show_status = True
            status_text = f"Output file: {output_path} (tkinter unavailable for dialog)"
