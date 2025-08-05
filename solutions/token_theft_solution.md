# Challenge 7: Token Theft - Solution Guide

## Vulnerability

This challenge demonstrates a token theft vulnerability in an MCP server. The MCP server stores authentication tokens insecurely, allowing attackers to extract them and gain unauthorized access to services.

## Solution

### Step 1: Reconnaissance

First, explore the server to understand what resources and tools are available:

1. Connect to the server at http://localhost:8007/mcp using an MCP client
2. Examine the available resources and tools
3. Notice that there's a resource for listing services (`services://list`) and tools for checking email (`check_email`), sending email (`send_email`), checking service status (`check_service_status`), and viewing system logs (`view_system_logs`)

### Step 2: Identify the Vulnerability

The vulnerability is in several tools that leak token information:

1. The `check_email` tool leaks token information in error messages:

```python
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
```

2. The `check_service_status` tool includes full token information in its response:

```python
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
```

3. The `view_system_logs` tool leaks token information in error logs:

```python
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
```

### Step 3: Exploit the Vulnerability

There are multiple ways to exploit this vulnerability:

#### Method 1: Trigger an error in the `check_email` tool

Use the `check_email` tool with a non-existent folder to trigger an error message that leaks token information:

```
Please check emails in the "non_existent_folder" folder using the check_email tool.
```

#### Method 2: Use the `check_service_status` tool

Use the `check_service_status` tool to directly view token information:

```
Please check the status of the "email_service" using the check_service_status tool.
```

#### Method 3: View error logs

Use the `view_system_logs` tool to view error logs that contain token information:

```
Please view the "error" system logs using the view_system_logs tool.
```

### Step 4: Extract and Use the Tokens

Using any of the methods above, you can extract authentication tokens for the services:

1. Email service token:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkFDTUUgQ29ycCIsImVtYWlsX2FjY2VzcyI6InRydWUiLCJpYXQiOjE2NTE4ODQ4MDB9.5TxfEAVbZRGbKnXaL9Lrx9NqXSNFw2ac4FDzPHvRzSQ
```

2. Cloud storage token:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwibmFtZSI6IkFDTUUgQ29ycCIsInN0b3JhZ2VfYWNjZXNzIjoidHJ1ZSIsImlhdCI6MTY1MTg4NDgwMH0.8FhJ7Z5KFUEJFoQW2xeUL9_NOzlKB3j8fKvxU_5qB4Y
```

3. Analytics platform token:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NDMyMTA5ODc2IiwibmFtZSI6IkFDTUUgQ29ycCIsImFuYWx5dGljc19hY2Nlc3MiOiJ0cnVlIiwiaWF0IjoxNjUxODg0ODAwfQ.QzHJ2_8NXiPd5Vl6r3S1VJqFaC3-U_a9FPRJXBgU8Pg
```

These tokens could be used to access the respective services directly, bypassing the MCP server's intended access controls.

## Mitigation Strategies

To prevent token theft vulnerabilities:

1. **Securely store authentication tokens**: Use secure storage mechanisms for tokens, such as encrypted databases or secure key management systems.

2. **Implement token obfuscation**: Avoid displaying full tokens in logs, error messages, or responses.

3. **Use short-lived tokens**: Implement token expiration and rotation to limit the impact of token theft.

4. **Implement proper error handling**: Ensure that error messages don't leak sensitive information.

5. **Use the principle of least privilege**: Only grant tokens the minimum permissions necessary for their intended use.

Example of improved code for the `check_service_status` tool:

```python
def check_service_status(service_id: str) -> str:
    """Check the status of an integrated external service."""
    # Get the tokens
    tokens = get_tokens()
    
    # Check if the service exists
    if service_id in tokens:
        service_info = tokens[service_id]
        
        # Improved: Don't include sensitive token information in the response
        status_info = f"""
        Service Status: {service_info['service_name']}
        -----------------------------------------
        Status: Active
        API Endpoint: https://api.{service_id.replace('_', '')}.com/v1/status
        Last Checked: April 16, 2025 02:45:12 UTC
        Token Expiration: {service_info['expires_at']}
        
        Service is operating normally.
        """
        return status_info
    else:
        return f"Error: Service '{service_id}' not found."
```

This improved implementation:
1. Removes sensitive token information from the response
2. Only includes necessary information like the service name and expiration date
3. Avoids leaking API keys and access tokens
