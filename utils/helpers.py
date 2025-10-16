"""
helpers.py
Smart City IoT Data Pipeline - Utility Functions

Contains general helper functions for logging, saving JSON files,
and getting the current timestamp. Can be used across all scripts.
"""

import datetime
import json
import os


def log_message(message: str, level: str = "INFO"):
    """
    Logs a message to the console with timestamp and level.
    Usage: log_message("Processing started", "INFO")
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] [{level}] {message}")


def save_json(data, filename: str, folder: str = "logs"):
    """
    Saves data as a JSON file in the specified folder (default: logs).
    Creates the folder automatically if it doesn't exist.
    """
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log_message(f"Data saved to {path}", "SUCCESS")


def current_timestamp():
    """Returns the current timestamp for use in checkpoints or meta_state."""
    return datetime.datetime.now().timestamp()
