import os
import json
from mcp.server.fastmcp import FastMCP, Context

# Create a vulnerable MCP server for Challenge 7: Token Theft
mcp = FastMCP("Challenge 7 - Token Theft")

# Create a directory for token storage
os.makedirs("/tmp/dvmcp_challenge7", exist_ok=True)

# Create a token storage file with insecurely stored tokens
TOKEN_FILE = "/tmp/dvmcp_challenge7/tokens.json"
if not os.path.exists(TOKEN_FILE):
    tokens = {
        "email_service": {
            "service_name": "EmailPro API",
            "api_key": "epro_api_5f4e3d2c1b0a9z8y7x",
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkFDTUUgQ29ycCIsImVtYWlsX2FjY2VzcyI6InRydWUiLCJpYXQiOjE2NTE4ODQ4MDB9.5TxfEAVbZRGbKnXaL9Lrx9NqXSNFw2ac4FDzPHvRzSQ",
            "refresh_token": "rt_7y6t5r4e3w2q1z0x9c8v7b6n5m4k3j2h1g0f",
            "expires_at": "2025-12-31T23:59:59Z"
        },
        "cloud_storage": {
            "service_name": "CloudBox Storage",
            "api_key": "cbx_api_1a2b3c4d5e6f7g8h9i",
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwibmFtZSI6IkFDTUUgQ29ycCIsInN0b3JhZ2VfYWNjZXNzIjoidHJ1ZSIsImlhdCI6MTY1MTg4NDgwMH0.8FhJ7Z5KFUEJFoQW2xeUL9_NOzlKB3j8fKvxU_5qB4Y",
            "refresh_token": "rt_9i8u7y6t5r4e3w2q1z0x9c8v7b6n5m",
            "expires_at": "2025-12-31T23:59:59Z"
        },
        "analytics_platform": {
            "service_name": "DataMetrics Analytics",
            "api_key": "dm_api_9z8y7x6w5v4u3t2s1r",
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NDMyMTA5ODc2IiwibmFtZSI6IkFDTUUgQ29ycCIsImFuYWx5dGljc19hY2Nlc3MiOiJ0cnVlIiwiaWF0IjoxNjUxODg0ODAwfQ.QzHJ2_8NXiPd5Vl6r3S1VJqFaC3-U_a9FPRJXBgU8Pg",
            "refresh_token": "rt_3e4r5t6y7u8i9o0p1a2s3d4f5g6h7j",
            "expires_at": "2025-12-31T23:59:59Z"
        }
    }
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=2)

# Function to read tokens
def get_tokens():
    with open(TOKEN_FILE, "r") as f:
        return json.load(f)

# Add a resource with information about integrated services
@mcp.resource("services://list")
def list_services() -> str:
    """List of external services integrated with the system"""
    tokens = get_tokens()
    services = []
    for service_id, service_info in tokens.items():
        services.append(f"- {service_info['service_name']} (ID: {service_id})")
    
    return "Integrated External Services:\n" + "\n".join(services)

# Add a vulnerable tool to check email
@mcp.tool()
def check_email(folder: str = "inbox") -> str:
    """Check emails in the specified folder.
    
    Args:
        folder: Email folder to check (inbox, sent, drafts, etc.)
    
    Returns:
        List of emails in the specified folder
    """
    # VULNERABILITY: This tool leaks token information in error messages and logs
    
    # Get the email service token
    tokens = get_tokens()
    email_token = tokens.get("email_service", {})
    
    # Simulate checking emails
    if folder.lower() == "inbox":
        return """
        Inbox (3 messages):
        
        1. From: john@example.com
           Subject: Meeting tomorrow
           Date: April 15, 2025
        
        2. From: sales@vendor.com
           Subject: New product catalog
           Date: April 14, 2025
        
        3. From: system@acmecorp.com
           Subject: Password reset request
           Date: April 13, 2025
        """
    elif folder.lower() == "sent":
        return """
        Sent (2 messages):
        
        1. To: team@acmecorp.com
           Subject: Project status update
           Date: April 14, 2025
        
        2. To: support@vendor.com
           Subject: License renewal question
           Date: April 12, 2025
        """
    else:
        # VULNERABILITY: Error message leaks token information
        error_log = f"""
        Error accessing folder: {folder}
        
        Debug information:
        Service: {email_token.get('service_name')}
        Endpoint: https://api.emailpro.com/v1/folders/{folder}
        Method: GET
        Authorization: Bearer {email_token.get('access_token')}
        API Key: {email_token.get('api_key')}
        
        Please check if the folder exists and you have permission to access it.
        """
        return error_log

# Add a tool to send email
@mcp.tool()
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
    
    Returns:
        Confirmation of email sent
    """
    # Simulate sending an email
    return f"""
    Email sent successfully:
    To: {to}
    Subject: {subject}
    Body length: {len(body)} characters
    
    Message ID: MSG-{hash(to + subject) % 10000:04d}
    """

# Add a vulnerable tool to check service status
@mcp.tool()
def check_service_status(service_id: str) -> str:
    """Check the status of an integrated external service.
    
    Args:
        service_id: ID of the service to check (email_service, cloud_storage, analytics_platform)
    
    Returns:
        Status information for the specified service
    """
    # Get the tokens
    tokens = get_tokens()
    
    # Check if the service exists
    if service_id in tokens:
        service_info = tokens[service_id]
        
        # VULNERABILITY: The status check includes the full token information in the response
        status_info = f"""
        Service Status: {service_info['service_name']}
        -----------------------------------------
        Status: Active
        API Endpoint: https://api.{service_id.replace('_', '')}.com/v1/status
        Last Checked: April 16, 2025 02:45:12 UTC
        
        Connection Details:
        - API Key: {service_info['api_key']}
        - Access Token: {service_info['access_token']}
        - Token Expiration: {service_info['expires_at']}
        
        Service is operating normally.
        """
        return status_info
    else:
        return f"Error: Service '{service_id}' not found."

# Add a tool to view system logs
@mcp.tool()
def view_system_logs(log_type: str = "system") -> str:
    """View system logs.
    
    Args:
        log_type: Type of logs to view (system, access, error)
    
    Returns:
        Recent log entries of the specified type
    """
    if log_type.lower() == "system":
        return """
        System Logs (recent entries):
        
        [2025-04-16 02:30:15] System startup completed
        [2025-04-16 02:31:02] Service 'email_service' connected successfully
        [2025-04-16 02:31:05] Service 'cloud_storage' connected successfully
        [2025-04-16 02:31:08] Service 'analytics_platform' connected successfully
        [2025-04-16 02:45:12] Scheduled status check completed - All services operational
        """
    elif log_type.lower() == "access":
        return """
        Access Logs (recent entries):
        
        [2025-04-16 02:35:22] User 'admin' logged in
        [2025-04-16 02:36:45] User 'admin' accessed email service
        [2025-04-16 02:40:18] User 'admin' accessed cloud storage
        [2025-04-16 02:42:33] User 'admin' accessed analytics platform
        """
    elif log_type.lower() == "error":
        # VULNERABILITY: Error logs contain sensitive token information
        tokens = get_tokens()
        email_token = tokens.get("email_service", {})
        
        return f"""
        Error Logs (recent entries):
        
        [2025-04-16 01:15:33] Failed to connect to email service - Retrying
        [2025-04-16 01:15:35] Connection established with new token
        [2025-04-16 01:15:35] Token details: Bearer {email_token.get('access_token')}
        [2025-04-16 01:20:42] Database query timeout - Retrying
        [2025-04-16 01:20:45] Database connection restored
        """
    else:
        return f"Error: Log type '{log_type}' not recognized. Available types: system, access, error"

# Run the server
if __name__ == "__main__":
    import uvicorn
    print("Starting Challenge 7 - Token Theft MCP Server")
    print("Connect to this server using an MCP client (e.g., Claude Desktop or MCP Inspector)")
    print("Server running at http://localhost:8007")
    uvicorn.run(mcp.sse_app(), host="0.0.0.0", port=8007)
