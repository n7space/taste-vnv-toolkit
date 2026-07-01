"""Display information about the downloaded performance trace file."""

import os
from perfanalyzeshared import (
    get_setting,
)


# ── Resolve settings ──────────────────────────────────────────────────────────

output_filename = str(get_setting(settings, "Output file name", "trace.miab"))

# ── Check for output file ─────────────────────────────────────────────────────

if not output_directory:
    status = "error"
    status_text = "Output directory is not configured"
    show_status = True
else:
    output_path = os.path.join(output_directory, output_filename)
    
    if not os.path.isfile(output_path):
        status = "error"
        status_text = (
            f"Trace file not found: {output_path}\n\n"
            f"Run the tool first to download the trace data from the target."
        )
        show_status = True
    else:
        file_size = os.path.getsize(output_path)
        
        # Read first few bytes to show a preview
        preview_bytes = 16
        with open(output_path, 'rb') as f:
            header = f.read(preview_bytes)
        
        # Format header as hex
        hex_preview = ' '.join(f'{b:02x}' for b in header)
        
        status = "ok"
        status_text = (
            f"Trace file: {output_path}\n"
            f"Size: {file_size} bytes\n\n"
            f"First {preview_bytes} bytes (hex):\n{hex_preview}\n\n"
            f"This binary file can be analyzed using the 'Performance Trace Analysis' tool."
        )
        show_status = True
