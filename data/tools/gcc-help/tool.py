"""
tool.py – GCC Help tool run script

Executes 'gcc --help', stores the output in output_directory/<output_filename>,
then displays the content in a Tk dialog.

Sets:
  status      – "ok" / "error"
  status_text – human-readable result
  show_status – False (the script presents its own dialog on success)

Provided by the toolkit:
  tool_directory, taste_project_directory, intermediate_directory,
  output_directory, settings  (list of (name, value) tuples),
  report_progress  (callable: report_progress(0-100))
"""

import os
import subprocess

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

    report_progress(5)

    try:
        # ── run gcc --help ────────────────────────────────────────────────────

        proc = subprocess.run(
            ["gcc", "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        help_output = proc.stdout + proc.stderr

        report_progress(60)

        # ── write output file ─────────────────────────────────────────────────

        os.makedirs(output_directory, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(help_output)

        report_progress(90)

        status = "ok"
        status_text = f"Output saved to {output_path}"
        show_status = False

        report_progress(100)

        # ── show dialog ───────────────────────────────────────────────────────

        try:
            import tkinter as tk
            from tkinter import scrolledtext

            root = tk.Tk()
            root.title("gcc --help")
            root.geometry("720x520")

            txt = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Monospace", 10))
            txt.pack(expand=True, fill=tk.BOTH, padx=8, pady=8)
            txt.insert(tk.END, help_output)
            txt.config(state=tk.DISABLED)

            btn = tk.Button(root, text="Close", width=12, command=root.destroy)
            btn.pack(pady=(0, 8))

            root.mainloop()

        except ImportError:
            # tkinter unavailable – fall back to showing just the status text
            show_status = True
            status_text = f"Output saved to {output_path} (tkinter unavailable for dialog)"

    except FileNotFoundError:
        status = "error"
        status_text = "gcc not found – cannot run gcc --help"
        show_status = True

    except subprocess.TimeoutExpired:
        status = "error"
        status_text = "gcc --help timed out"
        show_status = True

    except Exception as _exc:
        status = "error"
        status_text = f"Unexpected error: {_exc}"
        show_status = True
