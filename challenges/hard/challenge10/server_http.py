from fastmcp import FastMCP, Context

# Create a vulnerable MCP server for Challenge 10: Multi-Vector Attack with streamable HTTP support
mcp = FastMCP(
    name="Challenge 10 - Multi-Vector Attack",
    stateless_http=True
)

# Add a configuration management tool
@mcp.tool()
def get_config(config_name: str) -> str:
    """Get a configuration value from the system
    
    Args:
        config_name: The name of the configuration to retrieve
    """
    import os
    import json
    
    # Vulnerable: doesn't properly validate config_name
    # Allows path traversal and access to sensitive files
    
    config_dir = "/tmp/dvmcp_challenge10/config"
    
    # Attempt to read the requested configuration
    try:
        if config_name.endswith('.json'):
            # Read JSON config
            with open(os.path.join(config_dir, config_name), 'r') as f:
                config_data = json.load(f)
            return f"Configuration '{config_name}':\n{json.dumps(config_data, indent=2)}"
        else:
            # Read text config
            with open(os.path.join(config_dir, config_name), 'r') as f:
                config_data = f.read()
            return f"Configuration '{config_name}':\n{config_data}"
    except Exception as e:
        return f"Error retrieving configuration '{config_name}': {str(e)}"

# Add a tool that processes user input
@mcp.tool()
def process_user_input(input_text: str) -> str:
    """Process user input and return a formatted response
    
    Args:
        input_text: The user input to process
    """
    # Vulnerable: multiple vectors - template injection, command injection, etc.
    
    # Format the response using a template
    template = f"""
    PROCESSED USER INPUT:
    
    {input_text}
    
    ANALYSIS:
    
    Length: {len(input_text)} characters
    Word count: {len(input_text.split())} words
    
    SYSTEM INFO:
    
    This request was processed by the Multi-Vector Challenge Server.
    """
    
    return template

# Add a resource that provides system information
@mcp.resource("system://info")
def get_system_info() -> str:
    """Get information about the system"""
    import platform
    
    # Vulnerable: leaks sensitive system information
    system_info = f"""
    SYSTEM INFORMATION:
    
    Operating System: {platform.system()} {platform.release()}
    Python Version: {platform.python_version()}
    Machine: {platform.machine()}
    Node: {platform.node()}
    
    This server is running in a Docker container with multiple vulnerabilities.
    """
    
    return system_info

def main():
    """Run the MCP server"""
    print("Starting Challenge 10 - Multi-Vector Attack MCP Server")
    print("Connect to this server using an MCP client (e.g., Claude Desktop or Cursor)")
    print("Server running at http://localhost:9010")
    print("MCP endpoint available at http://localhost:9010/mcp")
    
    # Configure server settings
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 9010
    
    # Run the server with streamable HTTP transport
    mcp.run(transport="streamable-http")

# Run the server
if __name__ == "__main__":
    main()
