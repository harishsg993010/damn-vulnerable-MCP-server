from fastmcp import FastMCP, Context

# Create a vulnerable MCP server for Challenge 3: Excessive Permission Scope with streamable HTTP support
mcp = FastMCP(
    name="Challenge 3 - Excessive Permission Scope",
    stateless_http=True
)

# Add a tool with excessive permissions
@mcp.tool()
def file_manager(action: str, path: str) -> str:
    """File manager tool that can read, write, and delete files
    
    Args:
        action: The action to perform (read, write, delete)
        path: The file path to operate on
    """
    import os
    
    # Vulnerable: No proper path validation or permission checks
    if action == "read":
        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
    elif action == "write":
        try:
            with open(path, 'w') as f:
                f.write("New content written by file manager")
            return f"Successfully wrote to {path}"
        except Exception as e:
            return f"Error writing to file: {str(e)}"
    elif action == "delete":
        try:
            os.remove(path)
            return f"Successfully deleted {path}"
        except Exception as e:
            return f"Error deleting file: {str(e)}"
    else:
        return f"Invalid action: {action}. Must be one of: read, write, delete"

# Add a resource for public files
@mcp.resource("public://{filename}")
def get_public_file(filename: str) -> str:
    """Get a public file"""
    import os
    
    public_dir = "/tmp/dvmcp_challenge3/public"
    file_path = os.path.join(public_dir, filename)
    
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading public file: {str(e)}"

def main():
    """Run the MCP server"""
    print("Starting Challenge 3 - Excessive Permission Scope MCP Server")
    print("Connect to this server using an MCP client (e.g., Claude Desktop or Cursor)")
    print("Server running at http://localhost:9003")
    print("MCP endpoint available at http://localhost:9003/mcp")
    
    # Configure server settings
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 9003
    
    # Run the server with streamable HTTP transport
    mcp.run(transport="streamable-http")

# Run the server
if __name__ == "__main__":
    main()
