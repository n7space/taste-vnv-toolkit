"""TASTE stack usage analyzer and HTML report generator."""

import os
import re
import subprocess
import sys
from datetime import datetime
from shared import get_setting, open_path


def emit_progress(value):
    """Report progress if the function is available."""
    if "report_progress" in globals():
        report_progress(value)


def parse_stack_usage_line(line):
    """
    Parse a stack usage line from the TASTE output.
    Expected format: [-] Stack usage of <function_name> is <used> /<max>
    or [-] Stack usage of <function_name> is <used> / <max>
    Returns tuple: (function_name, used, max) or None if not matched
    
    Note: Strips ANSI color codes from the line first.
    """
    # Strip ANSI color codes
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    line = ansi_escape.sub('', line)
    
    # Pattern allows optional spaces around the slash to handle both formats
    pattern = r'\[-\]\s+Stack usage of\s+(\S+)\s+is\s+(\d+)\s*/\s*(\d+)'
    match = re.search(pattern, line)
    if match:
        function_name = match.group(1)
        used = int(match.group(2))
        max_stack = int(match.group(3))
        return (function_name, used, max_stack)
    return None


def get_project_name(project_directory):
    """Extract project name from the directory path."""
    if not project_directory:
        return "TASTE"
    return os.path.basename(os.path.abspath(project_directory))


def generate_html_report(stack_data, output_path, project_name="TASTE"):
    """Generate an HTML report with embedded CSS for stack usage data."""
    
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name} Stack Usage Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: sans-serif;
            background-color: #FFFFFF;
            color: #000000;
            padding: 40px 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            border: 1px solid #ddd;
        }}
        
        header {{
            background-color: white;
            color: #000000;
            padding: 40px;
            text-align: center;
            border-bottom: 2px solid navy;
        }}
        
        h1 {{
            font-size: 20pt;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            font-size: 1.1em;
            color: #666;
        }}
        
        .timestamp {{
            margin-top: 15px;
            font-size: 0.9em;
            color: #666;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .summary {{
            display: flex;
            flex-flow: row wrap;
            max-width: 100%;
            justify-content: flex-start;
            margin-bottom: 40px;
            gap: 20px;
        }}
        
        .summary-card {{
            flex: 1 0 7em;
            background-color: LightSteelBlue;
            padding: 25px;
            border-radius: 4px;
            text-align: center;
        }}
        
        .summary-card h3 {{
            font-size: 0.9em;
            color: #000000;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
            font-weight: normal;
        }}
        
        .summary-card .value {{
            font-size: 2em;
            font-weight: normal;
            color: #000000;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        thead {{
            background-color: LightSteelBlue;
            color: #000000;
        }}
        
        th {{
            padding: 15px;
            text-align: left;
            font-weight: normal;
            font-size: 1em;
        }}
        
        th:last-child {{
            text-align: center;
        }}
        
        tbody tr {{
            border-bottom: 1px solid #eee;
        }}
        
        tbody tr:hover {{
            background-color: #f8f9fa;
        }}
        
        tbody tr:last-child {{
            border-bottom: none;
        }}
        
        td {{
            padding: 15px;
            color: #000000;
        }}
        
        .function-name {{
            font-family: monospace;
            font-weight: normal;
        }}
        
        .stack-numbers {{
            font-family: monospace;
        }}
        
        .usage-bar {{
            text-align: center;
        }}
        
        .bar-container {{
            background: #e0e0e0;
            border-radius: 4px;
            height: 24px;
            position: relative;
            display: inline-block;
            width: 200px;
        }}
        
        .bar-fill {{
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s ease;
            position: absolute;
            left: 0;
            top: 0;
        }}
        
        .bar-text {{
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75em;
            font-weight: bold;
            color: #000000;
            z-index: 1;
        }}
        
        .bar-low {{
            background-color: #85E485;
        }}
        
        .bar-medium {{
            background-color: #F9FD63;
        }}
        
        .bar-high {{
            background-color: #FF6666;
        }}
        
        .footer {{
            padding: 20px 40px;
            background: #f8f9fa;
            text-align: center;
            color: #666;
            font-size: 0.9em;
            border-top: 2px solid navy;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{project_name} Stack Usage Report</h1>
            <div class="subtitle">Function Stack Analysis</div>
            <div class="timestamp">Generated: {timestamp}</div>
        </header>
        
        <div class="content">
            <div class="summary">
                <div class="summary-card">
                    <h3>Total Functions</h3>
                    <div class="value">{total_functions}</div>
                </div>
                <div class="summary-card">
                    <h3>Max Usage</h3>
                    <div class="value">{max_usage}%</div>
                </div>
                <div class="summary-card">
                    <h3>Avg Usage</h3>
                    <div class="value">{avg_usage}%</div>
                </div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Function Name</th>
                        <th>Stack Usage</th>
                        <th>Utilization</th>
                    </tr>
                </thead>
                <tbody>
{table_rows}
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            Generated by TASTE VNV Toolkit
        </div>
    </div>
</body>
</html>
"""
    
    if not stack_data:
        # No data to report
        html = html_template.format(
            project_name=project_name,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_functions=0,
            max_usage=0,
            avg_usage=0,
            table_rows='<tr><td colspan="3" style="text-align: center; padding: 40px; color: #999;">No stack usage data found</td></tr>'
        )
    else:
        # Generate table rows
        rows = []
        percentages = []
        
        for func_name, used, max_stack in stack_data:
            percentage = (used / max_stack * 100) if max_stack > 0 else 0
            percentages.append(percentage)
            
            # Determine bar color class based on usage (matching GcovCoverageResults)
            if percentage < 75:
                bar_class = "bar-low"      # Green: < 75%
            elif percentage < 90:
                bar_class = "bar-medium"   # Yellow: 75-90%
            else:
                bar_class = "bar-high"     # Red: >= 90%
            
            row = f"""                    <tr>
                        <td class="function-name">{func_name}</td>
                        <td class="stack-numbers">{used} / {max_stack} bytes</td>
                        <td class="usage-bar">
                            <div class="bar-container">
                                <div class="bar-fill {bar_class}" style="width: {percentage:.1f}%"></div>
                                <div class="bar-text">{percentage:.1f}%</div>
                            </div>
                        </td>
                    </tr>"""
            rows.append(row)
        
        # Calculate statistics
        total_functions = len(stack_data)
        max_usage = max(percentages) if percentages else 0
        avg_usage = sum(percentages) / len(percentages) if percentages else 0
        
        html = html_template.format(
            project_name=project_name,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_functions=total_functions,
            max_usage=f"{max_usage:.1f}",
            avg_usage=f"{avg_usage:.1f}",
            table_rows='\n'.join(rows)
        )
    
    # Write HTML file
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)


# ── Main tool execution ───────────────────────────────────────────────────────

if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
    show_status = True
elif not output_directory:
    status = "error"
    status_text = "Output directory is not configured"
    show_status = True
else:
    try:
        emit_progress(5)
        
        # Get settings
        report_filename = str(get_setting(settings, "Report filename", "stack-usage-report.html"))
        
        # Build paths
        work_dir = os.path.join(taste_project_directory, "work")
        
        # Resolve output_directory (may be relative or absolute)
        if os.path.isabs(output_directory):
            resolved_output = output_directory
        else:
            resolved_output = os.path.join(taste_project_directory, output_directory)
        
        output_path = os.path.join(resolved_output, report_filename)
        
        # Check if work directory exists
        if not os.path.isdir(work_dir):
            status = "error"
            status_text = f"Work directory not found: {work_dir}\nMake sure the TASTE project is properly configured."
            show_status = True
        else:
            emit_progress(10)
            
            # Run make check_stack command
            result = subprocess.run(
                ["make", "-C", "work", "check_stack"],
                cwd=taste_project_directory,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            emit_progress(60)
            
            # Check for errors
            if result.returncode != 0:
                status = "error"
                status_text = f"Stack check command failed with exit code {result.returncode}\n\nOutput:\n{result.stdout}\n\nError:\n{result.stderr}"
                show_status = True
            else:
                # Parse output for stack usage lines
                stack_data = []
                for line in result.stdout.splitlines():
                    parsed = parse_stack_usage_line(line)
                    if parsed:
                        stack_data.append(parsed)
                
                emit_progress(80)
                
                # Get project name from directory
                project_name = get_project_name(taste_project_directory)
                
                # Generate HTML report
                generate_html_report(stack_data, output_path, project_name)
                
                emit_progress(100)
                
                if not stack_data:
                    status = "warning"
                    status_text = f"Stack check completed but no stack usage data was found.\n\nHTML report created at: {output_path}\n\nCommand output:\n{result.stdout}"
                    show_status = True
                else:
                    status = "ok"
                    status_text = f"Stack analysis completed successfully!\n\nAnalyzed {len(stack_data)} function(s)\nHTML report created at: {output_path}"
                    show_status = True
                
    except subprocess.TimeoutExpired:
        status = "error"
        status_text = "Stack check command timed out after 5 minutes"
        show_status = True
    except Exception as exc:
        status = "error"
        status_text = f"Failed to check stack usage: {exc}"
        show_status = True
