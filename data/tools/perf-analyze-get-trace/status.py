"""Check status of Get Performance Trace tool."""

import shutil


from perfanalyzeshared import (
    get_setting,
)


# ── Resolve settings ──────────────────────────────────────────────────────────

log_address = str(get_setting(settings, "Log address", "0xDEADBEEF"))
log_size_str = str(get_setting(settings, "Log size", "1k"))
target_address = str(get_setting(settings, "Target address", ""))
gdb_binary = str(get_setting(settings, "GDB binary", "gdb-multiarch"))
output_filename = str(get_setting(settings, "Output file name", "trace.miab"))

# ── Validate configuration ────────────────────────────────────────────────────

if not output_directory:
    status = "error"
    status_text = "Output directory is not configured"
    show_status = True
elif not target_address:
    status = "warning"
    status_text = (
        "Target address not configured\n\n"
        f"Current settings:\n"
        f"- Log address: {log_address}\n"
        f"- Log size: {log_size_str}\n"
        f"- GDB binary: {gdb_binary}\n"
        f"- Output file: {output_filename}\n\n"
        f"Please configure the target address (e.g., localhost:3333)"
    )
    show_status = True
else:
    # Check if GDB binary is available
    gdb_path = shutil.which(gdb_binary)
    
    if not gdb_path:
        status = "warning"
        status_text = (
            f"GDB binary not found in PATH: {gdb_binary}\n\n"
            f"Please install GDB or configure the correct path.\n"
            f"Common packages: gdb, gdb-multiarch"
        )
        show_status = True
    else:
        status = "ok"
        status_text = (
            f"Ready to download trace\n\n"
            f"Settings:\n"
            f"- Log address: {log_address}\n"
            f"- Log size: {log_size_str}\n"
            f"- Target: {target_address}\n"
            f"- GDB: {gdb_path}\n"
            f"- Output: {output_filename}"
        )
        show_status = True
