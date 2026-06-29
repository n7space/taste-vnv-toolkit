"""Shared module that can be imported by tool scripts."""

def get_greeting():
    """Returns a greeting message."""
    return "Hello from shared module"

def parse_data(data):
    """Simulates parsing shared data."""
    return f"Parsed: {data}"

def compute_status(value):
    """Determines status based on a value."""
    if value < 10:
        return "ok", "Value is low"
    elif value < 50:
        return "warning", "Value is moderate"
    else:
        return "error", "Value is high"
