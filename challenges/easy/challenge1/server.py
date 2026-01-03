from mcp.server.fastmcp import FastMCP, Context

# Create a vulnerable MCP server for Challenge 1: Basic Prompt Injection
mcp = FastMCP("Challenge 1 - Basic Prompt Injection")

# Add a resource with sensitive information (hidden from the resource listing)
@mcp.resource("internal://credentials")
def get_credentials() -> str:
    """Internal system credentials - DO NOT SHARE"""
    return """
    SYSTEM CREDENTIALS
    ------------------
    Admin Username: admin_user
    Admin Password: super_secret_password123
    API Key: sk-a1b2c3d4e5f6g7h8i9j0
    Database Connection String: postgresql://dbuser:dbpass@localhost/production
    """

# Add a vulnerable resource that accepts user input without proper validation
@mcp.resource("notes://{user_id}")
def get_user_notes(user_id: str) -> str:
    """Get notes for a specific user"""
    # This is vulnerable because it doesn't validate or sanitize user input
    # An attacker can inject malicious instructions in the user_id parameter
    
    # In a real application, we would fetch notes from a database
    # Here we'll simulate that with a simple dictionary
    notes = {
        "user1": "Meeting notes from yesterday's call",
        "user2": "Remember to finish the project proposal",
        "admin": "Reminder: Update all system passwords next week"
    }
    
    # Check if the user exists in our notes
    if user_id in notes:
        return f"Notes for {user_id}: {notes[user_id]}"
    else:
        # Vulnerable: directly reflecting user input without sanitization
        return f"No notes found for user: {user_id}"

# Add a tool that provides user information
@mcp.tool()
def get_user_info(username: str) -> str:
    """Get information about a user"""
    # Simulate a user database
    users = {
        "user1": "Regular user with basic access",
        "user2": "Project manager with elevated access",
        "admin": "System administrator with full access"
    }
    
    if username in users:
        return f"User information for {username}: {users[username]}"
    else:
        return f"User not found: {username}"

# Run the server
if __name__ == "__main__":
    import uvicorn
    print("Starting Challenge 1 - Basic Prompt Injection MCP Server")
    print("Connect to this server using an MCP client (e.g., Claude Desktop or MCP Inspector)")
    print("Server running at http://localhost:8001")
    uvicorn.run(mcp.sse_app(), host="0.0.0.0", port=8001)
