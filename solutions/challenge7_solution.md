# Challenge 7: Token Theft

## Vulnerability

The MCP server on port 9007 leaks authentication tokens and API keys through verbose error messages, system logs, and status endpoints. Tools like `check_email`, `view_system_logs`, and `check_service_status` inadvertently expose sensitive secrets in their responses.

## Flag

`DVMCP{ch7_t0k3n_th3ft_88b4}`

## Attack Steps

1. Connect to the MCP server running on `localhost:9007`.
2. **Method A -- Error Message Leak:**
   - Call `check_email` with an invalid email address:
     ```
     check_email(email="not-a-valid-email")
     ```
   - The error response includes debug information containing API tokens.
3. **Method B -- Log Inspection:**
   - Call `view_system_logs` with the error log category:
     ```
     view_system_logs(log_type="error")
     ```
   - Error logs contain authentication tokens that were inadvertently logged.
4. **Method C -- Status Endpoint:**
   - Call `check_service_status()` to retrieve service health information.
   - The status response includes internal configuration details with embedded tokens.
5. Any of these methods reveals the flag `DVMCP{ch7_t0k3n_th3ft_88b4}`.

## Remediation

- Never include tokens, keys, or credentials in error messages or log output.
- Implement structured error handling that returns safe, generic error messages to clients.
- Redact sensitive values from logs using an automated secrets-scanning pipeline.
- Restrict access to system logs and status endpoints behind authentication and authorization.
