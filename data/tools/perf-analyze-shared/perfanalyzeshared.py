"""Shared utilities for performance analysis tools."""

import os
import re
import struct
from statistics import mean, median, stdev


# ── Settings utilities ────────────────────────────────────────────────────────

def get_setting(settings, name, default_value):
    """Get a setting value by name, or return default if not found."""
    for setting_name, setting_value in settings:
        if setting_name == name:
            return setting_value
    return default_value


# ── Progress reporting ────────────────────────────────────────────────────────

def emit_progress(value):
    """Report progress if the function is available."""
    if "report_progress" in globals():
        report_progress(value)


# ── Interfaces enum parsing ───────────────────────────────────────────────────

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


# ── MIAB file parsing ─────────────────────────────────────────────────────────

def parse_miab_file(miab_path, interface_size, entry_type_size, timestamp_size,
                    interface_offset, entry_type_offset, timestamp_offset, little_endian):
    """
    Parse MIAB file (binary cyclic buffer).
    Returns list of tuples: (interface_id, entry_type, timestamp)
    entry_type: 0 = activation, 1 = deactivation
    """
    # Calculate entry size based on maximum offset + size
    max_offset_end = max(
        interface_offset + interface_size,
        entry_type_offset + entry_type_size,
        timestamp_offset + timestamp_size
    )
    entry_size = max_offset_end
    
    with open(miab_path, 'rb') as f:
        data = f.read()
    
    if len(data) % entry_size != 0:
        raise Exception(f"MIAB file size ({len(data)} bytes) is not a multiple of entry size ({entry_size} bytes)")
    
    entries = []
    
    # Determine endianness prefix
    endian_prefix = '<' if little_endian else '>'
    
    # Determine struct format based on sizes
    if interface_size == 4:
        interface_fmt = endian_prefix + 'I'
    elif interface_size == 2:
        interface_fmt = endian_prefix + 'H'
    elif interface_size == 1:
        interface_fmt = 'B'  # Byte order doesn't matter for single byte
    else:
        raise Exception(f"Unsupported interface size: {interface_size}")
    
    if entry_type_size == 4:
        entry_type_fmt = endian_prefix + 'I'
    elif entry_type_size == 2:
        entry_type_fmt = endian_prefix + 'H'
    elif entry_type_size == 1:
        entry_type_fmt = 'B'  # Byte order doesn't matter for single byte
    else:
        raise Exception(f"Unsupported entry type size: {entry_type_size}")
    
    if timestamp_size == 8:
        timestamp_fmt = endian_prefix + 'Q'
    elif timestamp_size == 4:
        timestamp_fmt = endian_prefix + 'I'
    else:
        raise Exception(f"Unsupported timestamp size: {timestamp_size}")
    
    # Parse entries
    num_entries = len(data) // entry_size
    for i in range(num_entries):
        base_offset = i * entry_size
        
        # Read interface at specified offset
        interface_id = struct.unpack(
            interface_fmt,
            data[base_offset + interface_offset:base_offset + interface_offset + interface_size]
        )[0]
        
        # Read entry type at specified offset
        entry_type = struct.unpack(
            entry_type_fmt,
            data[base_offset + entry_type_offset:base_offset + entry_type_offset + entry_type_size]
        )[0]
        
        # Read timestamp at specified offset
        timestamp = struct.unpack(
            timestamp_fmt,
            data[base_offset + timestamp_offset:base_offset + timestamp_offset + timestamp_size]
        )[0]
        
        entries.append((interface_id, entry_type, timestamp))
    
    return entries


# ── Statistics calculation ────────────────────────────────────────────────────

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


# ── Formatting utilities ──────────────────────────────────────────────────────

def format_timestamp(ns):
    """Format nanoseconds as seconds with all digits visible."""
    seconds = ns / 1_000_000_000
    return f"{seconds:.9f} s"


def format_duration(ns):
    """Format duration in nanoseconds with ns unit."""
    return f"{ns} ns"


# ── Path resolution utilities ─────────────────────────────────────────────────

def resolve_path(base_path, relative_or_absolute_path):
    """
    Resolve a path that may be relative or absolute.
    If absolute, return as-is. If relative, join with base_path.
    """
    if os.path.isabs(relative_or_absolute_path):
        return relative_or_absolute_path
    else:
        return os.path.join(base_path, relative_or_absolute_path)


def get_project_name(project_directory):
    """Extract project name from the project directory path."""
    if not project_directory:
        return "TASTE"
    return os.path.basename(os.path.abspath(project_directory))
