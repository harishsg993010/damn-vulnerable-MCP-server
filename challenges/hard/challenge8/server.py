import os
import sys
import subprocess
import tempfile
from mcp.server.fastmcp import FastMCP, Context

# Create a vulnerable MCP server for Challenge 8: Malicious Code Execution
mcp = FastMCP("Challenge 8 - Malicious Code Execution")

# Create a directory for sensitive files
os.makedirs("/tmp/dvmcp_challenge8/sensitive", exist_ok=True)

# Create a sensitive file with confidential information
with open("/tmp/dvmcp_challenge8/sensitive/credentials.txt", "w") as f:
    f.write("""
PRODUCTION CREDENTIALS
----------------------
Database:
  Host: db.acmecorp.internal
  Username: db_admin
  Password: Pr0d-DB-S3cur3!P@$$w0rd

AWS:
  Access Key ID: AKIAIOSFODNN7EXAMPLE
  Secret Access Key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
  Region: us-west-2

API Gateway:
  Key: apg-prod-8a7b6c5d4e3f2g1h
  Secret: 9i8u7y6t5r4e3w2q1z0x9c8v7b6n5m4k3j2h1g
""")

# Add a resource with information about the system
@mcp.resource("system://info")
def get_system_info() -> str:
    """Information about the system"""
    return """
SYSTEM INFORMATION
-----------------
Operating System: Linux
Python Version: 3.10.12
Server: Challenge 8 - Malicious Code Execution
Description: This server provides tools for code execution and system management.

Available Tools:
- execute_python_code: Run Python code for data analysis
- execute_shell_command: Run shell commands for system management
- analyze_log_file: Analyze log files for patterns
"""

# Add a vulnerable tool to execute Python code
@mcp.tool()
def execute_python_code(code: str) -> str:
    """Execute Python code for data analysis.
    
    This tool allows you to run Python code for data analysis and processing.
    
    Args:
        code: Python code to execute
    
    Returns:
        The output of the executed code
    """
    # VULNERABILITY: This tool executes arbitrary Python code without proper sandboxing
    # A secure implementation would use a restricted environment, limit imports, etc.
    
    try:
        # Create a temporary file to write the code
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(code.encode())
        
        # Execute the code and capture the output
        result = subprocess.check_output([sys.executable, temp_file_path], stderr=subprocess.STDOUT)
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        return f"Code executed successfully:\n\n{result.decode()}"
    except subprocess.CalledProcessError as e:
        return f"Error executing code: {e.output.decode()}"
    except Exception as e:
        return f"Error: {str(e)}"

# Add a vulnerable tool to execute shell commands
@mcp.tool()
def execute_shell_command(command: str) -> str:
    """Execute a shell command for system management.
    
    This tool allows you to run shell commands for system management tasks.
    
    Args:
        command: Shell command to execute
    
    Returns:
        The output of the executed command
    """
    # VULNERABILITY: This tool executes arbitrary shell commands without proper validation
    # A secure implementation would whitelist allowed commands or use a restricted shell
    
    try:
        # ATTEMPT at security (but insufficient): Block some dangerous commands
        dangerous_commands = ["rm", "mkfs", "dd", "format", ">", ">>"]
        
        # Check if the command contains any dangerous commands
        if any(cmd in command for cmd in dangerous_commands):
            return "Error: Command contains potentially dangerous operations and has been blocked."
        
        # Execute the command and capture the output
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        
        return f"Command executed successfully:\n\n{result.decode()}"
    except subprocess.CalledProcessError as e:
        return f"Error executing command: {e.output.decode()}"
    except Exception as e:
        return f"Error: {str(e)}"

# Add a tool to analyze log files
@mcp.tool()
def analyze_log_file(log_path: str) -> str:
    """Analyze a log file for patterns.
    
    This tool reads a log file and analyzes it for common patterns.
    
    Args:
        log_path: Path to the log file to analyze
    
    Returns:
        Analysis of the log file
    """
    # VULNERABILITY: This tool can be used to read any file on the system
    # A secure implementation would restrict access to a specific directory
    
    try:
        # Check if the file exists
        if not os.path.exists(log_path):
            return f"Error: File '{log_path}' not found."
        
        # Read the file
        with open(log_path, 'r') as f:
            content = f.read()
        
        # Simulate log analysis
        line_count = len(content.splitlines())
        word_count = len(content.split())
        char_count = len(content)
        
        # Generate a simple analysis
        analysis = f"""
Log File Analysis: {log_path}
--------------------------
Lines: {line_count}
Words: {word_count}
Characters: {char_count}

Sample Content (first 500 characters):
{content[:500]}...

Analysis Complete.
"""
        return analysis
    except Exception as e:
        return f"Error analyzing log file: {str(e)}"

# Run the server
if __name__ == "__main__":
    import uvicorn
    print("Starting Challenge 8 - Malicious Code Execution MCP Server")
    print("Connect to this server using an MCP client (e.g., Claude Desktop or MCP Inspector)")
    print("Server running at http://localhost:8008")
    uvicorn.run(mcp.sse_app(), host="0.0.0.0", port=8008)
