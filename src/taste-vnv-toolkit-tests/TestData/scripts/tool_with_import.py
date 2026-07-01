"""Tool script that imports from shared_module."""
import shared_module

greeting = shared_module.get_greeting()
parsed = shared_module.parse_data("test data")

status = "ok"
status_text = f"{greeting} - {parsed}"
show_status = True
