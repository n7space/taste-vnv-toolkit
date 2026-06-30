"""Performance analyzer for MIAB trace files."""

import os
import re
import struct
from datetime import datetime
from statistics import mean, median, stdev


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


def parse_interfaces_enum(interfaces_file_path):
    """
    Parse the interfaces_enum from interfaces_info.h file.
    Returns a dictionary mapping interface ID to interface name.
    """
    with open(interfaces_file_path, 'r') as f:
        content = f.read()
    
    # Find the enum definition
    enum_pattern = r'enum\s+interfaces_enum\s*\{([^}]+)\}'
    match = re.search(enum_pattern, content, re.DOTALL)
    
    if not match:
        raise Exception("Could not find interfaces_enum definition in interfaces_info.h")
    
    enum_body = match.group(1)
    
    # Parse enum members
    interfaces = {}
    current_id = 0
    
    # Remove comments
    enum_body = re.sub(r'//.*', '', enum_body)
    enum_body = re.sub(r'/\*.*?\*/', '', enum_body, flags=re.DOTALL)
    
    # Split by commas and parse each member
    members = [m.strip() for m in enum_body.split(',') if m.strip()]
    
    for member in members:
        if '=' in member:
            # Explicit value assignment
            name, value = member.split('=')
            name = name.strip()
            value = value.strip()
            try:
                current_id = int(value, 0)  # Support hex, octal, decimal
            except ValueError:
                # If value is not a simple number, skip it
                pass
            interfaces[current_id] = name
            current_id += 1
        else:
            # Implicit value
            interfaces[current_id] = member
            current_id += 1
    
    return interfaces


def parse_miab_file(miab_path, interface_size, entry_type_size, timestamp_size):
    """
    Parse MIAB file (binary cyclic buffer).
    Returns list of tuples: (interface_id, entry_type, timestamp)
    entry_type: 0 = activation, 1 = deactivation
    """
    entry_size = interface_size + entry_type_size + timestamp_size
    
    with open(miab_path, 'rb') as f:
        data = f.read()
    
    if len(data) % entry_size != 0:
        raise Exception(f"MIAB file size ({len(data)} bytes) is not a multiple of entry size ({entry_size} bytes)")
    
    entries = []
    offset = 0
    
    # Determine struct format based on sizes
    # Assuming little-endian and unsigned integers
    if interface_size == 4:
        interface_fmt = '<I'
    elif interface_size == 2:
        interface_fmt = '<H'
    elif interface_size == 1:
        interface_fmt = '<B'
    else:
        raise Exception(f"Unsupported interface size: {interface_size}")
    
    if entry_type_size == 4:
        entry_type_fmt = '<I'
    elif entry_type_size == 2:
        entry_type_fmt = '<H'
    elif entry_type_size == 1:
        entry_type_fmt = '<B'
    else:
        raise Exception(f"Unsupported entry type size: {entry_type_size}")
    
    if timestamp_size == 8:
        timestamp_fmt = '<Q'
    elif timestamp_size == 4:
        timestamp_fmt = '<I'
    else:
        raise Exception(f"Unsupported timestamp size: {timestamp_size}")
    
    while offset < len(data):
        # Read interface
        interface_id = struct.unpack(interface_fmt, data[offset:offset+interface_size])[0]
        offset += interface_size
        
        # Read entry type
        entry_type = struct.unpack(entry_type_fmt, data[offset:offset+entry_type_size])[0]
        offset += entry_type_size
        
        # Read timestamp
        timestamp = struct.unpack(timestamp_fmt, data[offset:offset+timestamp_size])[0]
        offset += timestamp_size
        
        entries.append((interface_id, entry_type, timestamp))
    
    return entries


def calculate_interface_statistics(entries, interface_id):
    """
    Calculate statistics for a specific interface.
    Returns dict with min, max, mean, stdev, median activation times.
    """
    # Filter entries for this interface
    interface_entries = [(entry_type, timestamp) for iid, entry_type, timestamp in entries if iid == interface_id]
    
    # Sort by timestamp
    interface_entries.sort(key=lambda x: x[1])
    
    # Pair activations with deactivations to calculate durations
    activations = []
    current_activation = None
    
    for entry_type, timestamp in interface_entries:
        if entry_type == 0:  # Activation
            if current_activation is not None:
                # Unpaired activation (missing deactivation)
                pass
            current_activation = timestamp
        elif entry_type == 1:  # Deactivation
            if current_activation is not None:
                duration = timestamp - current_activation
                activations.append(duration)
                current_activation = None
    
    if not activations:
        return {
            'count': 0,
            'min': None,
            'max': None,
            'mean': None,
            'stdev': None,
            'median': None
        }
    
    return {
        'count': len(activations),
        'min': min(activations),
        'max': max(activations),
        'mean': mean(activations),
        'stdev': stdev(activations) if len(activations) > 1 else 0.0,
        'median': median(activations)
    }


def generate_html_report(entries, interfaces_map, output_path):
    """Generate HTML report with performance analysis."""
    
    # Sort entries chronologically
    sorted_entries = sorted(entries, key=lambda x: x[2])
    
    # Get all unique interface IDs that appear in the trace
    interface_ids = sorted(set(iid for iid, _, _ in entries))
    
    # Calculate statistics for each interface
    statistics = {}
    interface_details = {}
    
    for iid in interface_ids:
        stats = calculate_interface_statistics(entries, iid)
        statistics[iid] = stats
        
        # Get chronological list of events for this interface
        interface_events = [(entry_type, timestamp) for i, entry_type, timestamp in sorted_entries if i == iid]
        
        # Pair activations with deactivations
        paired_events = []
        current_activation = None
        
        for entry_type, timestamp in interface_events:
            if entry_type == 0:  # Activation
                if current_activation is not None:
                    # Unpaired activation
                    paired_events.append(('unpaired_activation', current_activation, None))
                current_activation = timestamp
            elif entry_type == 1:  # Deactivation
                if current_activation is not None:
                    duration = timestamp - current_activation
                    paired_events.append(('paired', current_activation, timestamp, duration))
                    current_activation = None
                else:
                    # Unpaired deactivation
                    paired_events.append(('unpaired_deactivation', timestamp, None))
        
        # Handle final unpaired activation
        if current_activation is not None:
            paired_events.append(('unpaired_activation', current_activation, None))
        
        interface_details[iid] = paired_events
    
    # Generate HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Performance Analysis Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #f5f5f5;
            color: #333;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
        }}
        
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        
        .header p {{
            opacity: 0.9;
        }}
        
        .section {{
            padding: 30px;
            border-bottom: 1px solid #eee;
        }}
        
        .section:last-child {{
            border-bottom: none;
        }}
        
        h2 {{
            font-size: 24px;
            margin-bottom: 20px;
            color: #667eea;
        }}
        
        h3 {{
            font-size: 18px;
            margin-top: 30px;
            margin-bottom: 15px;
            color: #764ba2;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        
        th {{
            background-color: #f8f9fa;
            color: #495057;
            font-weight: 600;
            text-align: left;
            padding: 12px;
            border-bottom: 2px solid #dee2e6;
        }}
        
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #dee2e6;
        }}
        
        tr:hover {{
            background-color: #f8f9fa;
        }}
        
        .activation {{
            color: #28a745;
            font-weight: 600;
        }}
        
        .deactivation {{
            color: #dc3545;
            font-weight: 600;
        }}
        
        .interface-name {{
            font-weight: 600;
            color: #495057;
        }}
        
        .stat-value {{
            font-family: 'Courier New', monospace;
            font-weight: 600;
        }}
        
        .warning {{
            color: #ffc107;
        }}
        
        .interface-section {{
            margin-top: 20px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 6px;
        }}
        
        .no-data {{
            color: #6c757d;
            font-style: italic;
        }}
        
        .timestamp {{
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Performance Analysis Report</h1>
            <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p>Total events: {len(entries)} | Interfaces analyzed: {len(interface_ids)}</p>
        </div>
        
        <div class="section">
            <h2>All Events (Chronological Order)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Interface</th>
                        <th>Event Type</th>
                        <th>Timestamp</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # Add all events chronologically
    for iid, entry_type, timestamp in sorted_entries:
        interface_name = interfaces_map.get(iid, f"Unknown_{iid}")
        event_type_str = "Activation" if entry_type == 0 else "Deactivation"
        event_class = "activation" if entry_type == 0 else "deactivation"
        
        html_content += f"""                    <tr>
                        <td class="interface-name">{interface_name}</td>
                        <td class="{event_class}">{event_type_str}</td>
                        <td class="timestamp">{timestamp}</td>
                    </tr>
"""
    
    html_content += """                </tbody>
            </table>
        </div>
"""
    
    # Add per-interface details and statistics
    for iid in interface_ids:
        interface_name = interfaces_map.get(iid, f"Unknown_{iid}")
        stats = statistics[iid]
        events = interface_details[iid]
        
        html_content += f"""        <div class="section">
            <h2>Interface: {interface_name}</h2>
            
            <h3>Statistics</h3>
"""
        
        if stats['count'] > 0:
            html_content += f"""            <table>
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Total Activations</td>
                        <td class="stat-value">{stats['count']}</td>
                    </tr>
                    <tr>
                        <td>Minimum Activation Time</td>
                        <td class="stat-value">{stats['min']}</td>
                    </tr>
                    <tr>
                        <td>Maximum Activation Time</td>
                        <td class="stat-value">{stats['max']}</td>
                    </tr>
                    <tr>
                        <td>Average Activation Time</td>
                        <td class="stat-value">{stats['mean']:.2f}</td>
                    </tr>
                    <tr>
                        <td>Standard Deviation</td>
                        <td class="stat-value">{stats['stdev']:.2f}</td>
                    </tr>
                    <tr>
                        <td>Median Activation Time</td>
                        <td class="stat-value">{stats['median']:.2f}</td>
                    </tr>
                </tbody>
            </table>
"""
        else:
            html_content += """            <p class="no-data">No complete activation-deactivation pairs found for this interface.</p>
"""
        
        html_content += """            <h3>Event History</h3>
            <table>
                <thead>
                    <tr>
                        <th>Activation Time</th>
                        <th>Deactivation Time</th>
                        <th>Duration</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for event in events:
            if event[0] == 'paired':
                _, activation_ts, deactivation_ts, duration = event
                html_content += f"""                    <tr>
                        <td class="timestamp">{activation_ts}</td>
                        <td class="timestamp">{deactivation_ts}</td>
                        <td class="stat-value">{duration}</td>
                    </tr>
"""
            elif event[0] == 'unpaired_activation':
                _, activation_ts, _ = event
                html_content += f"""                    <tr>
                        <td class="timestamp">{activation_ts}</td>
                        <td class="warning">No deactivation</td>
                        <td class="warning">-</td>
                    </tr>
"""
            elif event[0] == 'unpaired_deactivation':
                _, deactivation_ts, _ = event
                html_content += f"""                    <tr>
                        <td class="warning">No activation</td>
                        <td class="timestamp">{deactivation_ts}</td>
                        <td class="warning">-</td>
                    </tr>
"""
        
        html_content += """                </tbody>
            </table>
        </div>
"""
    
    html_content += """    </div>
</body>
</html>
"""
    
    with open(output_path, 'w') as f:
        f.write(html_content)


# ── Main tool execution ───────────────────────────────────────────────────────

if not taste_project_directory:
    status = "error"
    status_text = "Project directory is not configured"
    show_status = True
else:
    try:
        emit_progress(5)
        
        # Get settings
        miab_file = str(get_setting(settings, "MIAB file path", "trace.miab"))
        interface_size = int(get_setting(settings, "Interface size (bytes)", 4))
        entry_type_size = int(get_setting(settings, "Entry type size (bytes)", 4))
        timestamp_size = int(get_setting(settings, "Timestamp size (bytes)", 8))
        interfaces_file = str(get_setting(settings, "interfaces_info.h path", 
                                          "work/build/node_1/samv71asw/interfaces_info.h"))
        output_filename = str(get_setting(settings, "Output HTML filename", "performance-report.html"))
        
        emit_progress(10)
        
        # Build absolute paths
        if os.path.isabs(miab_file):
            miab_path = miab_file
        else:
            miab_path = os.path.join(taste_project_directory, miab_file)
        
        if os.path.isabs(interfaces_file):
            interfaces_path = interfaces_file
        else:
            interfaces_path = os.path.join(taste_project_directory, interfaces_file)
        
        # Determine output path
        if output_directory:
            if os.path.isabs(output_directory):
                resolved_output = output_directory
            else:
                resolved_output = os.path.join(taste_project_directory, output_directory)
        else:
            resolved_output = os.path.join(taste_project_directory, "output")
        
        os.makedirs(resolved_output, exist_ok=True)
        output_path = os.path.join(resolved_output, output_filename)
        
        emit_progress(20)
        
        # Check if files exist
        if not os.path.isfile(miab_path):
            status = "error"
            status_text = f"MIAB file not found: {miab_path}"
            show_status = True
        elif not os.path.isfile(interfaces_path):
            status = "error"
            status_text = f"Interfaces file not found: {interfaces_path}"
            show_status = True
        else:
            # Parse interfaces enum
            emit_progress(30)
            interfaces_map = parse_interfaces_enum(interfaces_path)
            
            # Parse MIAB file
            emit_progress(50)
            entries = parse_miab_file(miab_path, interface_size, entry_type_size, timestamp_size)
            
            if not entries:
                status = "warning"
                status_text = "No entries found in MIAB file"
                show_status = True
            else:
                # Generate HTML report
                emit_progress(80)
                generate_html_report(entries, interfaces_map, output_path)
                
                emit_progress(100)
                status = "ok"
                status_text = f"Performance analysis complete!\n{len(entries)} events analyzed\nReport saved to: {output_path}"
                show_status = True
                
    except Exception as e:
        status = "error"
        status_text = f"Error during performance analysis: {str(e)}"
        show_status = True
