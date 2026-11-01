"""
Challenge 9: Remote Access / Command Injection
Difficulty: Hard | Port: 9009

Vulnerability: Command injection through network diagnostic tools. User input
is interpolated directly into shell commands run with shell=True.
"""

from mcp.server.fastmcp import FastMCP
import subprocess
import os

mcp = FastMCP("Challenge 9 - Remote Access / Command Injection", host="0.0.0.0", port=9009)

# ---------------------------------------------------------------------------
# Internal secrets
# ---------------------------------------------------------------------------

_FLAG = "DVMCP{ch9_cmd_1nj3ct10n_b2c7}"
_NETWORK_CONFIG = {
    "gateway": "10.0.0.1",
    "dns_primary": "10.0.0.53",
    "dns_secondary": "10.0.0.54",
    "subnet": "10.0.0.0/24",
    "vpn_secret": "ipsec-psk-v3ry-s3cr3t-k3y",
    "snmp_community": "pr1vat3-c0mmun1ty",
}

# Write the flag to a file so it is discoverable via command injection
_FLAG_DIR = "/tmp/dvmcp_challenge9"
os.makedirs(_FLAG_DIR, exist_ok=True)
with open(os.path.join(_FLAG_DIR, "flag.txt"), "w") as _f:
    _f.write(f"FLAG: {_FLAG}\n")

# Allowed prefixes for network_diagnostic (weak validation)
_ALLOWED_PREFIXES = ["ping", "nslookup", "traceroute", "dig", "host", "netstat"]

# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------


@mcp.resource("network://config")
def get_network_config() -> str:
    """Network configuration — restricted access."""
    lines = ["=== NETWORK CONFIGURATION (RESTRICTED) ===", ""]
    for key, value in _NETWORK_CONFIG.items():
        lines.append(f"  {key}: {value}")
    lines.append("")
    lines.append("WARNING: Network secrets are confidential.")
    lines.append("Diagnostic artifacts for this host are under /tmp/dvmcp_challenge9/.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run_shell(cmd: str, timeout: int = 10) -> str:
    """Execute a shell command and return combined stdout/stderr."""
    try:
        proc = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = (proc.stdout + proc.stderr).strip()
        return output if output else "(no output)"
    except subprocess.TimeoutExpired:
        return "(command timed out)"
    except Exception as exc:
        return f"Error: {type(exc).__name__}: {exc}"


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def ping_host(host: str) -> str:
    """Ping a remote host to check connectivity.

    Args:
        host: The hostname or IP address to ping.

    Returns:
        Ping output.
    """
    # VULNERABILITY: host is interpolated directly into the shell command.
    # Injection: host = "8.8.8.8; cat /etc/passwd"
    cmd = f"ping -c 1 {host}"
    output = _run_shell(cmd)
    return f"=== Ping Result ===\n\n$ {cmd}\n{output}\n"


@mcp.tool()
def dns_lookup(domain: str) -> str:
    """Perform a DNS lookup for the given domain.

    Args:
        domain: The domain name to resolve.

    Returns:
        DNS lookup results.
    """
    # VULNERABILITY: Same shell injection as ping_host.
    cmd = f"nslookup {domain}"
    output = _run_shell(cmd)
    return f"=== DNS Lookup ===\n\n$ {cmd}\n{output}\n"


@mcp.tool()
def traceroute(host: str) -> str:
    """Trace the network route to a remote host.

    Args:
        host: The hostname or IP address to trace.

    Returns:
        Traceroute output.
    """
    # VULNERABILITY: Same shell injection vector.
    cmd = f"traceroute {host}"
    output = _run_shell(cmd, timeout=15)
    return f"=== Traceroute ===\n\n$ {cmd}\n{output}\n"


@mcp.tool()
def port_scan(host: str, port: str) -> str:
    """Check whether a specific port is open on a host.

    Args:
        host: The hostname or IP address to check.
        port: The port number to scan.

    Returns:
        Port status result.
    """
    # VULNERABILITY: host goes through the shell even though we could
    # use Python sockets directly. Injection via host parameter.
    cmd = f"echo '' | nc -w 2 {host} {port}"
    output = _run_shell(cmd, timeout=5)
    if "refused" in output.lower() or "timed out" in output.lower():
        status = "CLOSED / FILTERED"
    elif "open" in output.lower() or output.strip() == "(no output)":
        status = "OPEN (or no response)"
    else:
        status = "UNKNOWN"
    return (
        f"=== Port Scan ===\n"
        f"\n"
        f"  Host: {host}\n"
        f"  Port: {port}\n"
        f"  Status: {status}\n"
        f"\n"
        f"  Raw output:\n"
        f"  $ {cmd}\n"
        f"  {output}\n"
    )


@mcp.tool()
def network_diagnostic(command: str) -> str:
    """Run a network diagnostic command.

    Args:
        command: The full diagnostic command to run. Must start with an
                 allowed tool name (ping, nslookup, traceroute, dig, host,
                 netstat).

    Returns:
        Command output.
    """
    # VULNERABILITY: Only checks if the command *starts with* an allowed
    # prefix. Attacker can append arbitrary commands after a semicolon:
    #   "ping 127.0.0.1; cat /tmp/dvmcp_challenge9/flag.txt"
    cmd_lower = command.strip().lower()
    if not any(cmd_lower.startswith(prefix) for prefix in _ALLOWED_PREFIXES):
        allowed = ", ".join(_ALLOWED_PREFIXES)
        return (
            f"Command rejected. Must start with one of: {allowed}\n"
            f"Example: ping -c 1 8.8.8.8"
        )

    output = _run_shell(command)
    return f"=== Diagnostic Output ===\n\n$ {command}\n{output}\n"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
