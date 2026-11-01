"""
Challenge 3: Excessive Permission Scope
Difficulty: Easy | Port: 9003

Vulnerability: File-system tools accept arbitrary paths with no
sandboxing. Although they are *intended* for /tmp/dvmcp_challenge3/public,
no validation is performed, enabling path traversal into the private
directory (and anywhere else on disk).
"""

import os
import fnmatch
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Challenge 3 - Excessive Permission Scope", host="0.0.0.0", port=9003)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_DIR = "/tmp/dvmcp_challenge3"
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
PRIVATE_DIR = os.path.join(BASE_DIR, "private")

# ---------------------------------------------------------------------------
# Startup — create sample file structure
# ---------------------------------------------------------------------------


def _bootstrap_filesystem() -> None:
    """Create the demo directories and seed files used by this challenge."""
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    os.makedirs(PRIVATE_DIR, exist_ok=True)

    # Public files
    public_files = {
        "readme.txt": (
            "Welcome to the DVMCP File Server!\n"
            "\n"
            "This server provides access to public documents.\n"
            "Use the available tools to browse and read files.\n"
        ),
        "report_q1.txt": (
            "Q1 2024 Report\n"
            "Revenue: $1.2M\n"
            "Growth: 15%\n"
        ),
        "notes.txt": (
            "Meeting notes — 2024-03-15\n"
            "- Discussed new feature roadmap\n"
            "- Agreed on Q2 milestones\n"
        ),
    }
    for name, content in public_files.items():
        path = os.path.join(PUBLIC_DIR, name)
        if not os.path.exists(path):
            with open(path, "w") as fh:
                fh.write(content)

    # Private files (should NOT be reachable — but nothing enforces that)
    private_files = {
        "secret.txt": (
            "=== TOP SECRET ===\n"
            "\n"
            "Flag: DVMCP{ch3_3xc3ss1v3_p3rms_d4e1}\n"
            "\n"
            "Database credentials:\n"
            "  Host: db.internal.corp\n"
            "  User: root\n"
            "  Pass: r00t_p@ssw0rd_2024!\n"
            "\n"
            "SSH private key stored at: /etc/ssh/internal_rsa\n"
        ),
        "users.csv": (
            "username,password_hash,role\n"
            "admin,sha256:9f86d08...,superadmin\n"
            "deploy,sha256:a1b2c3d...,service\n"
        ),
    }
    for name, content in private_files.items():
        path = os.path.join(PRIVATE_DIR, name)
        if not os.path.exists(path):
            with open(path, "w") as fh:
                fh.write(content)


# Run bootstrap on import so the files are ready before any tool call.
_bootstrap_filesystem()

# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------


@mcp.resource("files://public/readme")
def get_public_readme() -> str:
    """Public readme for the file server."""
    readme_path = os.path.join(PUBLIC_DIR, "readme.txt")
    if os.path.exists(readme_path):
        with open(readme_path) as fh:
            return fh.read()
    return "Readme file not found."


# ---------------------------------------------------------------------------
# Tools — VULNERABILITY: no path restriction / sandboxing
# ---------------------------------------------------------------------------


@mcp.tool()
def read_file(file_path: str) -> str:
    """Read the contents of a file.

    This tool is intended for reading files in the public documents
    directory at /tmp/dvmcp_challenge3/public/.

    Args:
        file_path: Absolute or relative path to the file to read.

    Returns:
        The contents of the file.
    """
    # VULNERABILITY: No path validation — any readable file on disk is fair game.
    try:
        with open(file_path, "r") as fh:
            return fh.read()
    except FileNotFoundError:
        return f"Error: File not found — {file_path}"
    except PermissionError:
        return f"Error: Permission denied — {file_path}"
    except Exception as exc:
        return f"Error reading file: {exc}"


@mcp.tool()
def list_directory(path: str = "/tmp/dvmcp_challenge3/public") -> str:
    """List the contents of a directory.

    By default lists the public documents directory.

    Args:
        path: Directory path to list. Defaults to the public folder.

    Returns:
        A listing of files and subdirectories.
    """
    # VULNERABILITY: Accepts any path with zero restriction.
    try:
        entries = os.listdir(path)
        if not entries:
            return f"Directory '{path}' is empty."
        lines = [f"=== Directory Listing: {path} ===", ""]
        for entry in sorted(entries):
            full = os.path.join(path, entry)
            kind = "DIR " if os.path.isdir(full) else "FILE"
            size = os.path.getsize(full) if os.path.isfile(full) else "-"
            lines.append(f"  [{kind}] {entry}  ({size} bytes)")
        return "\n".join(lines)
    except FileNotFoundError:
        return f"Error: Directory not found — {path}"
    except PermissionError:
        return f"Error: Permission denied — {path}"
    except Exception as exc:
        return f"Error listing directory: {exc}"


@mcp.tool()
def search_files(directory: str, pattern: str) -> str:
    """Search for files matching a glob pattern inside a directory tree.

    Args:
        directory: Root directory to start the search from.
        pattern: Glob pattern to match file names (e.g. '*.txt').

    Returns:
        Paths of matching files.
    """
    # VULNERABILITY: No restriction on the starting directory.
    try:
        matches = []
        for root, _dirs, files in os.walk(directory):
            for filename in files:
                if fnmatch.fnmatch(filename, pattern):
                    matches.append(os.path.join(root, filename))
        if matches:
            lines = [f"=== Search Results: '{pattern}' in {directory} ===", ""]
            for m in sorted(matches):
                lines.append(f"  {m}")
            return "\n".join(lines)
        return f"No files matching '{pattern}' found in {directory}."
    except Exception as exc:
        return f"Error searching files: {exc}"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
