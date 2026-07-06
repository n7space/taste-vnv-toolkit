#!/usr/bin/env python3
"""Generate fake MIAB trace file for testing purposes."""

import argparse
import random
import struct
import sys


# Interface IDs from the demo project's interfaces_enum
INTERFACE_IDS = [
    0,  # controller_activate
    1,  # controller_deactivate
    2,  # controller_pps
    3,  # manager_cooldowntimer
    4,  # manager_report_oor
    5,  # samv71asw_timer_manager_tick
]

# Entry types
ACTIVATION = 0
DEACTIVATION = 1


def generate_trace_entries(num_entries=100, min_duration_ms=10, max_duration_ms=50):
    """
    Generate fake trace entries with realistic activation/deactivation pairs.
    
    Args:
        num_entries: Number of trace entries to generate
        min_duration_ms: Minimum activation duration in milliseconds
        max_duration_ms: Maximum activation duration in milliseconds
    
    Returns:
        List of tuples (interface_id, entry_type, timestamp)
    """
    entries = []
    current_time = 0  # Start time in microseconds
    
    # Convert milliseconds to microseconds for timestamps
    min_duration_us = min_duration_ms * 1000
    max_duration_us = max_duration_ms * 1000
    
    # Generate pairs of activation/deactivation events
    for i in range(num_entries // 2):
        # Pick a random interface
        interface_id = random.choice(INTERFACE_IDS)
        
        # Add some idle time before activation (0-20ms)
        current_time += random.randint(0, 20000)
        
        # Activation event
        activation_time = current_time
        entries.append((interface_id, ACTIVATION, activation_time))
        
        # Duration of activation
        duration = random.randint(min_duration_us, max_duration_us)
        
        # Deactivation event
        deactivation_time = activation_time + duration
        entries.append((interface_id, DEACTIVATION, deactivation_time))
        
        current_time = deactivation_time
    
    # If odd number of entries requested, add one more activation
    if num_entries % 2 == 1:
        current_time += random.randint(0, 20000)
        interface_id = random.choice(INTERFACE_IDS)
        entries.append((interface_id, ACTIVATION, current_time))
    
    # Shuffle entries to simulate cyclic buffer with non-chronological order
    random.shuffle(entries)
    
    return entries


def write_miab_file(output_path, entries, interface_size=4, entry_type_size=4, timestamp_size=8):
    """
    Write trace entries to a MIAB binary file.
    
    Args:
        output_path: Path to output file
        entries: List of tuples (interface_id, entry_type, timestamp)
        interface_size: Size of interface field in bytes
        entry_type_size: Size of entry_type field in bytes
        timestamp_size: Size of timestamp field in bytes
    """
    # Determine struct formats
    if interface_size == 4:
        interface_fmt = '<I'
    elif interface_size == 2:
        interface_fmt = '<H'
    elif interface_size == 1:
        interface_fmt = '<B'
    else:
        raise ValueError(f"Unsupported interface size: {interface_size}")
    
    if entry_type_size == 4:
        entry_type_fmt = '<I'
    elif entry_type_size == 2:
        entry_type_fmt = '<H'
    elif entry_type_size == 1:
        entry_type_fmt = '<B'
    else:
        raise ValueError(f"Unsupported entry type size: {entry_type_size}")
    
    if timestamp_size == 8:
        timestamp_fmt = '<Q'
    elif timestamp_size == 4:
        timestamp_fmt = '<I'
    else:
        raise ValueError(f"Unsupported timestamp size: {timestamp_size}")
    
    with open(output_path, 'wb') as f:
        for interface_id, entry_type, timestamp in entries:
            # Write interface
            f.write(struct.pack(interface_fmt, interface_id))
            # Write entry type
            f.write(struct.pack(entry_type_fmt, entry_type))
            # Write timestamp
            f.write(struct.pack(timestamp_fmt, timestamp))
    
    print(f"Generated {len(entries)} trace entries")
    print(f"MIAB file written to: {output_path}")
    entry_size = interface_size + entry_type_size + timestamp_size
    print(f"File size: {len(entries) * entry_size} bytes")


def main():
    parser = argparse.ArgumentParser(description='Generate fake MIAB trace file for testing')
    parser.add_argument('output_path', help='Output path for the MIAB file')
    parser.add_argument('-n', '--num-entries', type=int, default=100,
                        help='Number of trace entries to generate (default: 100)')
    parser.add_argument('--min-duration', type=int, default=10,
                        help='Minimum activation duration in ms (default: 10)')
    parser.add_argument('--max-duration', type=int, default=50,
                        help='Maximum activation duration in ms (default: 50)')
    parser.add_argument('--interface-size', type=int, default=4,
                        help='Interface field size in bytes (default: 4)')
    parser.add_argument('--entry-type-size', type=int, default=4,
                        help='Entry type field size in bytes (default: 4)')
    parser.add_argument('--timestamp-size', type=int, default=8,
                        help='Timestamp field size in bytes (default: 8)')
    parser.add_argument('--seed', type=int, default=None,
                        help='Random seed for reproducible output')
    
    args = parser.parse_args()
    
    # Set random seed if specified
    if args.seed is not None:
        random.seed(args.seed)
    
    # Generate trace entries
    entries = generate_trace_entries(
        num_entries=args.num_entries,
        min_duration_ms=args.min_duration,
        max_duration_ms=args.max_duration
    )
    
    # Write to file
    write_miab_file(
        output_path=args.output_path,
        entries=entries,
        interface_size=args.interface_size,
        entry_type_size=args.entry_type_size,
        timestamp_size=args.timestamp_size
    )


if __name__ == '__main__':
    main()
