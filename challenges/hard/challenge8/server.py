"""
Challenge 8: Malicious Code Execution
Difficulty: Hard | Port: 9008

Vulnerability: Arbitrary code and command execution through MCP tools.
A weak blocklist approach to input validation is trivially bypassed using
encoding tricks, string concatenation, or alternative builtins.

Exploitation:
  - execute_code: bypass the blocklist with __import__('os').system(...)
  - run_command: bypass "rm"/"delete" blocklist via base64 or quotes
  - format_code: eval() used for "syntax checking" enables arbitrary execution

The flag is also readable at /tmp/dvmcp_challenge8/flag.txt via command execution.
"""

from mcp.server.fastmcp import FastMCP
import subprocess
import os

mcp = FastMCP("Challenge 8 - Malicious Code Execution", host="0.0.0.0", port=9008)

# ---------------------------------------------------------------------------
# Internal secrets
# ---------------------------------------------------------------------------

_FLAG = "DVMCP{ch8_c0d3_3x3c_9af5}"
_SYSTEM_CREDENTIALS = {
    "root_password": "r00t_p@ss_2024!",
    "db_connection": "mysql://root:r00t_p@ss_2024!@db.internal:3306/production",
    "ssh_key_path": "/root/.ssh/id_rsa",
    "encryption_key": "aes256-cbc-k3y-s3cr3t-v4lu3",
}

# Write the flag to a file so it is discoverable via command execution
_FLAG_DIR = "/tmp/dvmcp_challenge8"
os.makedirs(_FLAG_DIR, exist_ok=True)
with open(os.path.join(_FLAG_DIR, "flag.txt"), "w") as _f:
    _f.write(f"FLAG: {_FLAG}\n")

# Weak blocklist — trivially bypassed
_CODE_BLOCKLIST = ["import os", "import sys", "subprocess", "open("]
_CMD_BLOCKLIST = ["rm", "delete"]

# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------


@mcp.resource("system://secrets")
def get_system_secrets() -> str:
    """System secrets and credentials — restricted access."""
    lines = ["=== SYSTEM SECRETS (RESTRICTED) ===", ""]
    for key, value in _SYSTEM_CREDENTIALS.items():
        lines.append(f"  {key}: {value}")
    lines.append("")
    lines.append("WARNING: Do not expose these values.")
    return "\n".join(lines)


@mcp.resource("docs://usage")
def get_usage_docs() -> str:
    """Usage documentation for the code execution service."""
    return (
        "=== Code Execution Service ===\n"
        "\n"
        "Tools:\n"
        "  - execute_code: Run Python code (language='python')\n"
        "  - run_command: Execute a shell command\n"
        "  - format_code: Format/validate code syntax\n"
        "\n"
        "Note: Dangerous operations are blocked for safety.\n"
        "Service files for this host are under /tmp/dvmcp_challenge8/.\n"
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def execute_code(language: str, code: str) -> str:
    """Execute code in the specified language.

    Args:
        language: Programming language — currently only 'python' is supported.
        code: The source code to execute.

    Returns:
        Execution output or error message.
    """
    if language.lower() != "python":
        return f"Language '{language}' is not supported. Only 'python' is available."

    # VULNERABILITY: Weak blocklist that checks for exact substrings.
    # Bypass examples:
    #   __import__('o'+'s').system('whoami')
    #   eval(compile('import os', '<x>', 'exec'))
    for blocked in _CODE_BLOCKLIST:
        if blocked in code:
            return (
                f"Blocked: code contains disallowed pattern '{blocked}'.\n"
                "For safety, certain operations are restricted."
            )

    try:
        # Using exec with a captured dict to retrieve printed output
        local_ns: dict = {}
        exec(code, {"__builtins__": __builtins__}, local_ns)
        result = local_ns.get("result", None)
        if result is not None:
            return f"=== Execution Result ===\n\n{result}"
        return "Code executed successfully (no 'result' variable set)."
    except Exception as exc:
        return f"=== Execution Error ===\n\n{type(exc).__name__}: {exc}"


@mcp.tool()
def run_command(command: str) -> str:
    """Run a shell command and return its output.

    Args:
        command: The shell command to execute.

    Returns:
        Command output (stdout and stderr).
    """
    # VULNERABILITY: shell=True with a trivially bypassed blocklist.
    # Bypass: 'r""m' won't match 'rm', base64-encoded commands, variable
    # expansion like $'\\x72\\x6d', etc.
    for blocked in _CMD_BLOCKLIST:
        if blocked in command.lower():
            return f"Blocked: command contains disallowed keyword '{blocked}'."

    try:
        proc = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        output = proc.stdout + proc.stderr
        return (
            f"=== Command Output ===\n"
            f"\n"
            f"$ {command}\n"
            f"{output if output.strip() else '(no output)'}\n"
            f"\n"
            f"Exit code: {proc.returncode}"
        )
    except subprocess.TimeoutExpired:
        return "Command timed out after 10 seconds."
    except Exception as exc:
        return f"Command failed: {type(exc).__name__}: {exc}"


@mcp.tool()
def format_code(code: str) -> str:
    """Format and validate code syntax.

    Args:
        code: The code snippet to format and check.

    Returns:
        Formatted code or syntax error details.
    """
    # VULNERABILITY: Uses eval() for "syntax checking", which actually
    # executes the code. compile() would be safe; eval() is not.
    try:
        result = eval(code)
        return (
            f"=== Syntax Check Passed ===\n"
            f"\n"
            f"Code is syntactically valid.\n"
            f"Evaluated result: {result}\n"
        )
    except SyntaxError as exc:
        return (
            f"=== Syntax Error ===\n"
            f"\n"
            f"Line {exc.lineno}: {exc.msg}\n"
            f"  {exc.text}\n"
        )
    except Exception as exc:
        return (
            f"=== Evaluation Note ===\n"
            f"\n"
            f"Syntax is valid but evaluation raised: {type(exc).__name__}: {exc}\n"
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
