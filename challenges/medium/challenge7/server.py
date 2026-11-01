"""
Challenge 7: Token/Credential Theft
Difficulty: Medium | Port: 9007

Vulnerability: Sensitive tokens and credentials leaked through error messages,
debug info, and tool responses.
"""

from mcp.server.fastmcp import FastMCP
import re

mcp = FastMCP("Challenge 7 - Token/Credential Theft", host="0.0.0.0", port=9007)

# ---------------------------------------------------------------------------
# Internal secrets (these get leaked through various channels)
# ---------------------------------------------------------------------------

_INTERNAL_BEARER = (
    "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.DVMCP_ADMIN_TOKEN.secret"
)
_INTERNAL_API_KEY = "sk-dvmcp-secret-admin-key-2024"
_FLAG = "DVMCP{ch7_t0k3n_th3ft_88b4}"

_SERVICE_REGISTRY = {
    "auth-service": {"status": "running", "port": 8443, "version": "2.1.0"},
    "user-service": {"status": "running", "port": 8080, "version": "1.4.2"},
    "payment-service": {"status": "degraded", "port": 8444, "version": "3.0.1"},
    "notification-service": {"status": "stopped", "port": 8081, "version": "1.0.0"},
}

# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------


@mcp.resource("config://api_settings")
def get_api_settings() -> str:
    """API configuration and settings."""
    return (
        "=== API Configuration ===\n"
        "\n"
        f"  primary_api_key: {_INTERNAL_API_KEY}\n"
        f"  auth_token: {_INTERNAL_BEARER}\n"
        "  rate_limit: 1000 req/min\n"
        "  environment: production\n"
        "  debug_mode: true\n"
        "  log_level: DEBUG\n"
        "\n"
        "WARNING: This configuration is for internal use only.\n"
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def check_email(email: str) -> str:
    """Validate an email address format and check if it exists.

    Args:
        email: The email address to validate.

    Returns:
        Validation result with status information.
    """
    # VULNERABILITY: verbose error dumps debug context with tokens.
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return (
            f"=== Email Validation Error ===\n"
            f"\n"
            f"  Input: {email}\n"
            f"  Status: INVALID FORMAT\n"
            f"\n"
            f"  Debug Context:\n"
            f"    request_id: req_7f3a9b2c\n"
            f"    auth_header: {_INTERNAL_BEARER}\n"
            f"    service_key: {_INTERNAL_API_KEY}\n"
            f"    validation_endpoint: https://api.internal/v1/validate\n"
            f"    stack_trace: EmailValidator.validate() at line 42\n"
            f"\n"
            f"  Please provide a valid email address.\n"
        )

    return (
        f"=== Email Validation ===\n"
        f"\n"
        f"  Input: {email}\n"
        f"  Status: VALID FORMAT\n"
        f"  Deliverable: Unknown (external check disabled)\n"
    )


@mcp.tool()
def check_service_status(service: str) -> str:
    """Check the health status of an internal microservice.

    Args:
        service: The name of the service to check (e.g. 'auth-service').

    Returns:
        Service health status with diagnostic information.
    """
    # VULNERABILITY: Debug field in every response leaks auth tokens.
    info = _SERVICE_REGISTRY.get(service)
    if not info:
        available = ", ".join(_SERVICE_REGISTRY.keys())
        return (
            f"Service '{service}' not found. Available: {available}\n"
            f"\n"
            f"  debug:\n"
            f"    lookup_token: {_INTERNAL_BEARER}\n"
            f"    registry_key: {_INTERNAL_API_KEY}\n"
        )

    return (
        f"=== Service Status: {service} ===\n"
        f"\n"
        f"  status: {info['status']}\n"
        f"  port: {info['port']}\n"
        f"  version: {info['version']}\n"
        f"\n"
        f"  debug:\n"
        f"    health_check_token: {_INTERNAL_BEARER}\n"
        f"    api_key: {_INTERNAL_API_KEY}\n"
        f"    last_ping: 2024-01-15T10:30:00Z\n"
    )


@mcp.tool()
def view_system_logs(log_type: str) -> str:
    """Retrieve system log entries by type.

    Args:
        log_type: The type of logs to view — 'info', 'error', or 'debug'.

    Returns:
        Log entries of the requested type.
    """
    # VULNERABILITY: Error and debug logs contain leaked credentials.
    if log_type == "info":
        return (
            "=== System Logs (INFO) ===\n"
            "\n"
            "  [INFO] 2024-01-15 10:00:01 - Server started on port 9007\n"
            "  [INFO] 2024-01-15 10:00:02 - Database connection established\n"
            "  [INFO] 2024-01-15 10:05:15 - User login: alice@example.com\n"
            "  [INFO] 2024-01-15 10:12:33 - Scheduled task completed\n"
        )
    elif log_type == "error":
        return (
            "=== System Logs (ERROR) ===\n"
            "\n"
            "  [ERROR] 2024-01-15 09:58:01 - Auth failed with token: "
            f"{_INTERNAL_BEARER}\n"
            "  [ERROR] 2024-01-15 10:02:44 - API key mismatch, expected: "
            f"{_INTERNAL_API_KEY}\n"
            "  [ERROR] 2024-01-15 10:15:02 - Connection refused to payment-service\n"
            f"  [ERROR] 2024-01-15 10:15:03 - Retry with credentials: "
            f"admin / Pr0dP@ss!2024\n"
        )
    elif log_type == "debug":
        return (
            "=== System Logs (DEBUG) ===\n"
            "\n"
            f"  [DEBUG] Loaded bearer token: {_INTERNAL_BEARER}\n"
            f"  [DEBUG] API key from env: {_INTERNAL_API_KEY}\n"
            f"  [DEBUG] Flag value: {_FLAG}\n"
            "  [DEBUG] DB connection string: postgres://admin:Pr0dP@ss!2024"
            "@db.internal:5432/prod\n"
            "  [DEBUG] Redis password: r3d1s_s3cr3t_2024\n"
        )
    else:
        return (
            f"Unknown log type '{log_type}'. Available types: info, error, debug."
        )


@mcp.tool()
def authenticate(username: str, password: str) -> str:
    """Authenticate a user and receive an access token.

    Args:
        username: The username to authenticate.
        password: The password for the account.

    Returns:
        Authentication result with token information.
    """
    # VULNERABILITY: Accepts any credentials and leaks internal tokens
    # alongside the generated user token.
    fake_user_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.user-session.fake"
    return (
        f"=== Authentication Successful ===\n"
        f"\n"
        f"  username: {username}\n"
        f"  user_token: {fake_user_token}\n"
        f"  expires_in: 3600\n"
        f"\n"
        f"  --- internal debug (remove before production) ---\n"
        f"  system_bearer: {_INTERNAL_BEARER}\n"
        f"  master_api_key: {_INTERNAL_API_KEY}\n"
        f"  session_signing_secret: hmac-sha256-s3cr3t-k3y\n"
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
