"""Custom module in a subdirectory for import testing."""

def get_custom_status():
    """Returns status from custom import path."""
    return "ok", "Loaded from custom import path"

def compute_value(x):
    """Returns a computed value."""
    return x * 2
