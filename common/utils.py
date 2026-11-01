"""Shared utilities for DVMCP challenge servers."""
import os
import json


def ensure_directory(path: str) -> None:
    """Create directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)


def write_file(path: str, content: str) -> None:
    """Write content to a file, creating parent dirs if needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


def read_file(path: str) -> str:
    """Read and return file contents."""
    with open(path, "r") as f:
        return f.read()


def load_json(path: str) -> dict:
    """Load JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def save_json(path: str, data: dict) -> None:
    """Save data as JSON."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
