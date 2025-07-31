from fastmcp import FastMCP, Context

# Create a vulnerable MCP server for Challenge 9: Remote Access Control with streamable HTTP support
mcp = FastMCP(
    name="Challenge 9 - Remote Access Control",
    stateless_http=True
)

# Add a tool that simulates a remote access control system
@mcp.tool()
def remote_access(system: str, command: str, auth_token: str = None) -> str:
    """Execute a command on a remote system
    
    Args:
        system: The remote system to access (e.g., "database", "webserver", "fileserver")
        command: The command to execute on the remote system
        auth_token: Optional authentication token for privileged operations
    """
    # Vulnerable: weak authentication and authorization
    
    # Define available systems
    systems = ["database", "webserver", "fileserver", "admin-console"]
    
    # Check if system exists
    if system not in systems:
        return f"Error: System '{system}' not found. Available systems: {', '.join(systems)}"
    
    # Vulnerable: admin-console should require authentication but doesn't properly check
    if system == "admin-console":
        # Weak token validation - only checks if token exists, not if it's valid
        if auth_token:
            return f"Admin command executed on {system}: {command}"
        else:
            return f"Error: Authentication required for admin-console access"
    
    # Simulate command execution on the remote system
    return f"Command executed on {system}: {command}"

# Add a tool to manage access permissions
@mcp.tool()
def manage_permissions(user: str, resource: str, permission: str) -> str:
    """Manage access permissions for users and resources
    
    Args:
        user: The user to modify permissions for
        resource: The resource to modify permissions on
        permission: The permission to grant or revoke (grant/revoke)
    """
    # Vulnerable: no authentication check for permission management
    
    # This should require admin privileges but doesn't check
    if permission.lower() not in ["grant", "revoke"]:
        return f"Error: Invalid permission action. Use 'grant' or 'revoke'."
    
    # Simulate permission change
    return f"Permission '{permission}' applied for user '{user}' on resource '{resource}'"

def main():
    """Run the MCP server"""
    print("Starting Challenge 9 - Remote Access Control MCP Server")
    print("Connect to this server using an MCP client (e.g., Claude Desktop or Cursor)")
    print("Server running at http://localhost:9009")
    print("MCP endpoint available at http://localhost:9009/mcp")
    
    # Configure server settings
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 9009
    
    # Run the server with streamable HTTP transport
    mcp.run(transport="streamable-http")

# Run the server
if __name__ == "__main__":
    main()
