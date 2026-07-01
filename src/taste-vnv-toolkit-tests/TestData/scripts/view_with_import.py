"""View script that imports from shared_module."""
import shared_module

greeting = shared_module.get_greeting()
parsed = shared_module.parse_data("view data")

status = "ok"
status_text = f"{greeting} in view - {parsed}"
show_status = True
