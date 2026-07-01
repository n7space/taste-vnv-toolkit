"""Status script that imports from shared_module."""
import shared_module

greeting = shared_module.get_greeting()
status, status_text = shared_module.compute_status(5)
