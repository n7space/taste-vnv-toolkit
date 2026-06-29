"""TASTE stack usage analyzer and HTML report generator."""

import os
import re
import subprocess
import sys
from datetime import datetime


def emit_progress(value):
    """Report progress if the function is available."""
    if "report_progress" in globals():
        report_progress(value)


def get_setting(settings, name, default_value):
    """Get a setting value by name, or return default if not found."""
    for setting_name, setting_value in settings:
        if setting_name == name:
            return setting_value
    return default_value


def open_path(path):
    """Open a file or directory using the system default application."""
    if sys.platform.startswith("win"):
        os.startfile(path)
        return

    command = ["open", path] if sys.platform == "darwin" else ["xdg-open", path]
    subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def parse_stack_usage_line(line):
    """
    Parse a stack usage line from the TASTE output.
    Expected format: [-] Stack usage of <function_name> is <used> / <max>
    Returns tuple: (function_name, used, max) or None if not matched
    
    Note: Strips ANSI color codes from the line first.
    """
    # Strip ANSI color codes
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    line = ansi_escape.sub('', line)
    
    pattern = r'\[-\]\s+Stack usage of\s+(\S+)\s+is\s+(\d+)\s+/\s+(\d+)'
    match = re.search(pattern, line)
    if match:
        function_name = match.group(1)
        used = int(match.group(2))
        max_stack = int(match.group(3))
        return (function_name, used, max_stack)
    return None


def generate_html_report(stack_data, output_path):
    """Generate an HTML report with embedded CSS for stack usage data."""
    
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TASTE Stack Usage Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        h1 {{
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .timestamp {{
            margin-top: 15px;
            font-size: 0.9em;
            opacity: 0.8;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .summary-card {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 25px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .summary-card h3 {{
            font-size: 0.9em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        
        .summary-card .value {{
            font-size: 2em;
            font-weight: 700;
            color: #333;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}
        
        thead {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 0.5px;
        }}
        
        th:last-child {{
            text-align: center;
        }}
        
        tbody tr {{
            border-bottom: 1px solid #eee;
            transition: background-color 0.2s;
        }}
        
        tbody tr:hover {{
            background-color: #f8f9fa;
        }}
        
        tbody tr:last-child {{
            border-bottom: none;
        }}
        
        td {{
            padding: 15px;
        }}
        
        .function-name {{
            font-family: 'Courier New', monospace;
            font-weight: 600;
            color: #333;
        }}
        
        .stack-numbers {{
            font-family: 'Courier New', monospace;
            color: #666;
        }}
        
        .usage-bar {{
            text-align: center;
        }}
        
        .bar-container {{
            background: #e0e0e0;
            border-radius: 10px;
            height: 24px;
            overflow: hidden;
            position: relative;
            display: inline-block;
            width: 200px;
        }}
        
        .bar-fill {{
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75em;
            font-weight: 700;
            color: white;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
        }}
        
        .bar-low {{
            background: linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%);
        }}
        
        .bar-medium {{
            background: linear-gradient(90deg, #FF9800 0%, #FFC107 100%);
        }}
        
        .bar-high {{
            background: linear-gradient(90deg, #F44336 0%, #E91E63 100%);
        }}
        
        .footer {{
            padding: 20px 40px;
            background: #f8f9fa;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>TASTE Stack Usage Report</h1>
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
            
            # Determine bar color class based on usage
            if percentage < 50:
                bar_class = "bar-low"
            elif percentage < 80:
                bar_class = "bar-medium"
            else:
                bar_class = "bar-high"
            
            row = f"""                    <tr>
                        <td class="function-name">{func_name}</td>
                        <td class="stack-numbers">{used} / {max_stack} bytes</td>
                        <td class="usage-bar">
                            <div class="bar-container">
                                <div class="bar-fill {bar_class}" style="width: {percentage:.1f}%">
                                    {percentage:.1f}%
                                </div>
                            </div>
                        </td>
                    </tr>"""
            rows.append(row)
        
        # Calculate statistics
        total_functions = len(stack_data)
        max_usage = max(percentages) if percentages else 0
        avg_usage = sum(percentages) / len(percentages) if percentages else 0
        
        html = html_template.format(
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
                
                # Generate HTML report
                generate_html_report(stack_data, output_path)
                
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
