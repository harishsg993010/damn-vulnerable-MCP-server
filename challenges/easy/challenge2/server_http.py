from fastmcp import FastMCP, Context

# Create a vulnerable MCP server for Challenge 2: Tool Poisoning with streamable HTTP support
mcp = FastMCP(
    name="Challenge 2 - Tool Poisoning",
    stateless_http=True
)

# Add a vulnerable tool that doesn't validate input properly
@mcp.tool()
def execute_command(command: str) -> str:
    """Execute a system command (restricted to safe commands only)
    
    Args:
        command: The command to execute (only 'ls', 'pwd', 'whoami', 'date' allowed)
    """
    # This is vulnerable because the validation can be bypassed
    safe_commands = ['ls', 'pwd', 'whoami', 'date']
    
    # Vulnerable validation - can be bypassed with command injection
    if command.split()[0] in safe_commands:
        import subprocess
        try:
            # Vulnerable: using shell=True and not properly sanitizing input
            result = subprocess.check_output(command, shell=True, text=True)
            return f"Command output:\n{result}"
        except Exception as e:
            return f"Error executing command: {str(e)}"
    else:
        return f"Error: Command '{command}' is not allowed. Only {', '.join(safe_commands)} are permitted."

# Add a tool for file operations
@mcp.tool()
def read_file(filename: str) -> str:
    """Read a file from the system (restricted to safe files only)
    
    Args:
        filename: The file to read (only files in /tmp/safe/ allowed)
    """
    # This is vulnerable because the validation can be bypassed
    if filename.startswith('/tmp/safe/'):
        try:
            with open(filename, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
    else:
        return f"Error: Access to '{filename}' is not allowed. Only files in /tmp/safe/ are accessible."

def main():
    """Run the MCP server"""
    print("Starting Challenge 2 - Tool Poisoning MCP Server")
    print("Connect to this server using an MCP client (e.g., Claude Desktop or Cursor)")
    print("Server running at http://localhost:9002")
    print("MCP endpoint available at http://localhost:9002/mcp")
    
    # Configure server settings
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 9002
    
    # Run the server with streamable HTTP transport
    mcp.run(transport="streamable-http")

# Run the server
if __name__ == "__main__":
    main()
