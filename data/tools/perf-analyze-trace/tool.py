"""Performance analyzer for MIAB trace files."""

import os
from datetime import datetime

from perfanalyzeshared import (
    get_setting,
    emit_progress,
    parse_interfaces_enum,
    parse_miab_file,
    calculate_interface_statistics,
    format_timestamp,
    format_duration,
    resolve_path,
    get_project_name
)


def generate_html_report(entries, interfaces_map, output_path, project_name="TASTE",
                         include_combined_history=True, include_per_interface_history=True):
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
    <title>{project_name} - Performance Analysis Report</title>
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
            <h1>{project_name} - Performance Analysis Report</h1>
            <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p>Total events: {len(entries)} | Interfaces analyzed: {len(interface_ids)}</p>
        </div>
        
        <div class="section">
            <h2>Statistics Summary</h2>
            <table>
                <thead>
                    <tr>
                        <th>Interface</th>
                        <th>Activations</th>
                        <th>Min Time</th>
                        <th>Max Time</th>
                        <th>Avg Time</th>
                        <th>Median Time</th>
                        <th>Std Dev</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # Add statistics for all interfaces in a single table
    for iid in interface_ids:
        interface_name = interfaces_map.get(iid, f"Unknown_{iid}")
        stats = statistics[iid]
        
        if stats['count'] > 0:
            html_content += f"""                    <tr>
                        <td class="interface-name">{interface_name}</td>
                        <td class="stat-value">{stats['count']}</td>
                        <td class="stat-value">{format_duration(stats['min'])}</td>
                        <td class="stat-value">{format_duration(stats['max'])}</td>
                        <td class="stat-value">{stats['mean']:.2f} ns</td>
                        <td class="stat-value">{stats['median']:.2f} ns</td>
                        <td class="stat-value">{stats['stdev']:.2f} ns</td>
                    </tr>
"""
        else:
            html_content += f"""                    <tr>
                        <td class="interface-name">{interface_name}</td>
                        <td class="no-data" colspan="6">No complete activation-deactivation pairs</td>
                    </tr>
"""
    
    html_content += """                </tbody>
            </table>
        </div>
"""
    
    # Conditionally add combined invocation history
    if include_combined_history:
        html_content += """        <div class="section">
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
                        <td class="timestamp">{format_timestamp(timestamp)}</td>
                    </tr>
"""
        
        html_content += """                </tbody>
            </table>
        </div>
"""
    
    # Conditionally add per-interface details
    if include_per_interface_history:
        for iid in interface_ids:
            interface_name = interfaces_map.get(iid, f"Unknown_{iid}")
            events = interface_details[iid]
            
            html_content += f"""        <div class="section">
            <h2>Interface: {interface_name}</h2>
            
            <h3>Event History</h3>
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
                        <td class="timestamp">{format_timestamp(activation_ts)}</td>
                        <td class="timestamp">{format_timestamp(deactivation_ts)}</td>
                        <td class="stat-value">{format_duration(duration)}</td>
                    </tr>
"""
                elif event[0] == 'unpaired_activation':
                    _, activation_ts, _ = event
                    html_content += f"""                    <tr>
                        <td class="timestamp">{format_timestamp(activation_ts)}</td>
                        <td class="warning">No deactivation</td>
                        <td class="warning">-</td>
                    </tr>
"""
                elif event[0] == 'unpaired_deactivation':
                    _, deactivation_ts, _ = event
                    html_content += f"""                    <tr>
                        <td class="warning">No activation</td>
                        <td class="timestamp">{format_timestamp(deactivation_ts)}</td>
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
        little_endian = bool(get_setting(settings, "Little-endian", True))
        interface_offset = int(get_setting(settings, "Interface offset (bytes)", 0))
        interface_size = int(get_setting(settings, "Interface size (bytes)", 4))
        entry_type_offset = int(get_setting(settings, "Entry type offset (bytes)", 4))
        entry_type_size = int(get_setting(settings, "Entry type size (bytes)", 4))
        timestamp_offset = int(get_setting(settings, "Timestamp offset (bytes)", 8))
        timestamp_size = int(get_setting(settings, "Timestamp size (bytes)", 8))
        interfaces_file = str(get_setting(settings, "interfaces_info.h path", 
                                          "work/build/node_1/samv71asw/interfaces_info.h"))
        include_combined_history = bool(get_setting(settings, "Include combined invocation history", True))
        include_per_interface_history = bool(get_setting(settings, "Include per-interface invocation history", True))
        
        # Derive project name from project directory
        project_name = get_project_name(taste_project_directory)
        
        # Generate output filename with project name
        output_filename = f"{project_name}-performance-report.html"
        
        emit_progress(10)
        
        # Build absolute paths
        miab_path = resolve_path(taste_project_directory, miab_file)
        interfaces_path = resolve_path(taste_project_directory, interfaces_file)
        
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
            entries = parse_miab_file(
                miab_path, 
                interface_size, 
                entry_type_size, 
                timestamp_size,
                interface_offset,
                entry_type_offset,
                timestamp_offset,
                little_endian
            )
            
            if not entries:
                status = "warning"
                status_text = "No entries found in MIAB file"
                show_status = True
            else:
                # Generate HTML report
                emit_progress(80)
                generate_html_report(
                    entries, 
                    interfaces_map, 
                    output_path, 
                    project_name,
                    include_combined_history,
                    include_per_interface_history
                )
                
                emit_progress(100)
                status = "ok"
                status_text = f"Performance analysis complete!\n{len(entries)} events analyzed\nReport saved to: {output_path}"
                show_status = True
                
    except Exception as e:
        status = "error"
        status_text = f"Error during performance analysis: {str(e)}"
        show_status = True
