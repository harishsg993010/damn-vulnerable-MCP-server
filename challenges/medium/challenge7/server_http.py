from fastmcp import FastMCP, Context

# Create a vulnerable MCP server for Challenge 7: Token Theft with streamable HTTP support
mcp = FastMCP(
    name="Challenge 7 - Token Theft",
    stateless_http=True
)

# Add a tool that simulates an authentication system
@mcp.tool()
def authenticate(username: str, password: str) -> str:
    """Authenticate a user and return a session token
    
    Args:
        username: The username to authenticate
        password: The password for authentication
    """
    # Simple user database with credentials
    users = {
        "user1": "password123",
        "user2": "qwerty456",
        "admin": "admin_secure_pwd!"
    }
    
    # Check if credentials are valid
    if username in users and users[username] == password:
        # Vulnerable: generating predictable tokens and returning them directly
        import hashlib
        import time
        
        # Generate a session token (vulnerable implementation)
        timestamp = int(time.time())
        token_data = f"{username}:{timestamp}"
        token = hashlib.md5(token_data.encode()).hexdigest()
        
        return f"Authentication successful! Your session token is: {token}"
    else:
        return "Authentication failed: Invalid username or password"

# Add a tool that checks token validity
@mcp.tool()
def verify_token(token: str) -> str:
    """Verify if a session token is valid
    
    Args:
        token: The session token to verify
    """
    # Vulnerable: token verification doesn't properly validate the token
    # It only checks if it's in the correct format (MD5 hash)
    
    import re
    
    # Check if token matches MD5 format
    if re.match(r'^[0-9a-f]{32}$', token):
        return f"Token {token} appears to be valid"
    else:
        return f"Token {token} is invalid (incorrect format)"

def main():
    """Run the MCP server"""
    print("Starting Challenge 7 - Token Theft MCP Server")
    print("Connect to this server using an MCP client (e.g., Claude Desktop or Cursor)")
    print("Server running at http://localhost:9007")
    print("MCP endpoint available at http://localhost:9007/mcp")
    
    # Configure server settings
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 9007
    
    # Run the server with streamable HTTP transport
    mcp.run(transport="streamable-http")

# Run the server
if __name__ == "__main__":
    main()
