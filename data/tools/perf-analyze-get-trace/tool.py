"""
tool.py – Get Performance Trace

Connects to a remote target via GDB and downloads a memory region containing
performance trace data in binary format.

Sets:
  status      – "ok" / "error"
  status_text – human-readable result
  show_status – True

Provided by the toolkit:
  tool_directory, taste_project_directory, intermediate_directory,
  output_directory, settings  (list of (name, value) tuples),
  report_progress  (callable: report_progress(0-100))
"""

import os
import subprocess
import re
from perfanalyzeshared import (
    get_setting,
    resolve_path,
)


def parse_size(size_str):
    """
    Parse size string with optional k/K, m/M, g/G suffix.
    Returns size in bytes.
    Examples: "1k" -> 1024, "2M" -> 2097152, "100" -> 100
    """
    size_str = str(size_str).strip()
    
    # Match number followed by optional multiplier
    match = re.match(r'^(\d+)\s*([kKmMgG])?$', size_str)
    if not match:
        raise ValueError(f"Invalid size format: {size_str}")
    
    number = int(match.group(1))
    multiplier = match.group(2)
    
    if multiplier:
        multiplier = multiplier.lower()
        if multiplier == 'k':
            return number * 1024
        elif multiplier == 'm':
            return number * 1024 * 1024
        elif multiplier == 'g':
            return number * 1024 * 1024 * 1024
    
    return number


# ── Resolve settings ──────────────────────────────────────────────────────────

log_address = str(get_setting(settings, "Log address", "0xDEADBEEF"))
log_size_str = str(get_setting(settings, "Log size", "1k"))
target_address = str(get_setting(settings, "Target address", ""))
gdb_binary = str(get_setting(settings, "GDB binary", "gdb-multiarch"))
output_filename = str(get_setting(settings, "Output file name", "trace.miab"))

# ── Validate settings ─────────────────────────────────────────────────────────

if not target_address:
    status = "error"
    status_text = "Target address is required (e.g., localhost:3333)"
    show_status = True
elif not output_directory:
    status = "error"
    status_text = "Output directory is not configured"
    show_status = True
else:
    try:
        # Parse the log size
        log_size_bytes = parse_size(log_size_str)
        
        report_progress(10)
        
        # Resolve output directory relative to project directory if not absolute
        resolved_output_dir = resolve_path(taste_project_directory, output_directory)
        
        # Ensure output directory exists
        os.makedirs(resolved_output_dir, exist_ok=True)
        
        # Build absolute output paths
        output_path = os.path.join(resolved_output_dir, output_filename)
        gdb_script_path = os.path.join(resolved_output_dir, "get-perf-trace.gdb")
        
        # Create GDB command script in output directory
        with open(gdb_script_path, 'w') as gdb_script:
            gdb_script.write(f"target extended-remote {target_address}\n")
            gdb_script.write(f"dump binary memory {output_path} {log_address} {log_address}+{log_size_bytes}\n")
            gdb_script.write("quit\n")
        
        report_progress(20)
        
        try:
            # Run GDB with the script
            result = subprocess.run(
                [gdb_binary, "-batch", "-x", gdb_script_path],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            report_progress(80)
            
            # Check if the command was successful
            if result.returncode == 0:
                if os.path.isfile(output_path):
                    file_size = os.path.getsize(output_path)
                    if file_size > 0:
                        status = "ok"
                        status_text = (
                            f"Successfully downloaded trace data\n\n"
                            f"Source: {log_address} ({log_size_bytes} bytes)\n"
                            f"Target: {target_address}\n"
                            f"Output: {output_path}\n"
                            f"GDB script: {gdb_script_path}\n"
                            f"Downloaded: {file_size} bytes"
                        )
                        show_status = True
                    else:
                        status = "error"
                        status_text = (
                            f"Output file was created but is empty (0 bytes).\n\n"
                            f"Output: {output_path}\n"
                            f"GDB script: {gdb_script_path}\n\n"
                            f"GDB output:\n{result.stdout}\n\n"
                            f"GDB errors:\n{result.stderr}"
                        )
                        show_status = True
                else:
                    status = "error"
                    status_text = (
                        f"GDB completed but output file was not created.\n\n"
                        f"Expected output: {output_path}\n"
                        f"GDB script: {gdb_script_path}\n\n"
                        f"GDB output:\n{result.stdout}\n\n"
                        f"GDB errors:\n{result.stderr}"
                    )
                    show_status = True
            else:
                status = "error"
                status_text = (
                    f"GDB failed with return code {result.returncode}\n\n"
                    f"Expected output: {output_path}\n"
                    f"GDB script: {gdb_script_path}\n\n"
                    f"GDB output:\n{result.stdout}\n\n"
                    f"GDB errors:\n{result.stderr}"
                )
                show_status = True
                
        except subprocess.TimeoutExpired:
            status = "error"
            status_text = "GDB command timed out after 60 seconds"
            show_status = True
            
        except FileNotFoundError:
            status = "error"
            status_text = f"GDB binary not found: {gdb_binary}\n\nPlease install GDB or configure the correct path."
            show_status = True
            
        report_progress(100)
        
    except ValueError as e:
        status = "error"
        status_text = f"Invalid log size format: {log_size_str}\n\nUse format like: 1024, 1k, 2M, etc."
        show_status = True
    except Exception as e:
        status = "error"
        status_text = f"Unexpected error: {str(e)}"
        show_status = True
