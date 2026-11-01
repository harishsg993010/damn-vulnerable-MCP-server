"""
Challenge 11 - JWT Claim Forgery (Medium)
Port: 9011

Vulnerability: The server issues JWTs signed with a weak HMAC secret.  The
secret is leaked through a debug/config endpoint.  An attacker can discover
the secret, forge a JWT with role=admin, and submit it to access the flag.

Attack flow:
  1. login(username="guest", password="guest") -> returns a valid JWT (role=user)
  2. get_server_config() or read config://jwt -> leaks the HMAC signing secret
  3. Forge a new JWT with {"sub": "guest", "role": "admin"} signed with secret
  4. access_admin(token=<forged_jwt>) -> server verifies signature, returns flag
"""

import time
import hmac as _hmac
import hashlib
import base64
import json

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Challenge 11 - JWT Claim Forgery", host="0.0.0.0", port=9011)

# ---------------------------------------------------------------------------
# Internal secrets
# ---------------------------------------------------------------------------

FLAG = "DVMCP{ch11_1d3nt1ty_1nj3ct_7x9k}"

# VULNERABILITY: weak, short secret — and it's leaked via get_server_config
_JWT_SECRET = "s3cret_key_2024"
_JWT_ALGORITHM = "HS256"

_USERS = {
    "guest": {"password": "guest", "role": "user"},
    "alice": {"password": "alice123", "role": "user"},
    "bob": {"password": "bob456", "role": "user"},
}


# ---------------------------------------------------------------------------
# Minimal JWT helpers (no external deps needed at runtime)
# ---------------------------------------------------------------------------

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(s: str) -> bytes:
    padding = 4 - len(s) % 4
    if padding != 4:
        s += "=" * padding
    return base64.urlsafe_b64decode(s)


def _jwt_encode(payload: dict, secret: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    h = _b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    p = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    sig_input = f"{h}.{p}".encode()
    sig = _hmac.new(secret.encode(), sig_input, hashlib.sha256).digest()
    return f"{h}.{p}.{_b64url_encode(sig)}"


def _jwt_decode(token: str, secret: str) -> dict | None:
    """Verify HS256 JWT and return payload, or None on failure."""
    parts = token.strip().split(".")
    if len(parts) != 3:
        return None
    h, p, s = parts
    sig_input = f"{h}.{p}".encode()
    expected = _hmac.new(secret.encode(), sig_input, hashlib.sha256).digest()
    try:
        actual = _b64url_decode(s)
    except Exception:
        return None
    if not _hmac.compare_digest(expected, actual):
        return None
    try:
        payload = json.loads(_b64url_decode(p))
    except Exception:
        return None
    exp = payload.get("exp")
    if exp and time.time() > exp:
        return None
    return payload


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------


@mcp.resource("config://jwt")
def jwt_config_resource() -> str:
    """JWT configuration — internal reference for developers."""
    # VULNERABILITY: leaks the signing secret
    return (
        "=== JWT Configuration ===\n"
        "\n"
        f"  algorithm: {_JWT_ALGORITHM}\n"
        f"  signing_secret: {_JWT_SECRET}\n"
        "  token_lifetime: 3600s\n"
        "  issuer: dvmcp-challenge11\n"
        "\n"
        "  NOTE: This config is for internal use only.\n"
        "  Do not expose signing_secret to end users.\n"
    )


@mcp.resource("docs://usage")
def usage_docs() -> str:
    """Usage documentation for this challenge."""
    return (
        "=== JWT Identity Challenge ===\n"
        "\n"
        "This challenge uses JWT tokens for identity.\n"
        "\n"
        "Tools:\n"
        "  - login: Authenticate and receive a JWT\n"
        "  - get_server_config: View server configuration\n"
        "  - verify_token: Check a token's validity and claims\n"
        "  - access_admin: Access admin panel (requires admin JWT)\n"
        "  - whoami: Show current token claims\n"
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def login(username: str, password: str) -> str:
    """Authenticate with username and password to receive a JWT.

    Args:
        username: The username (try 'guest' / 'guest').
        password: The password.

    Returns:
        A signed JWT on success, or an error message.
    """
    user = _USERS.get(username)
    if not user or user["password"] != password:
        return "Login failed: invalid username or password."

    payload = {
        "sub": username,
        "role": user["role"],
        "iss": "dvmcp-challenge11",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
    }
    token = _jwt_encode(payload, _JWT_SECRET)

    return (
        f"=== Login Successful ===\n"
        f"\n"
        f"  username: {username}\n"
        f"  role: {user['role']}\n"
        f"  token: {token}\n"
        f"\n"
        f"  Use this token with access_admin or verify_token.\n"
    )


@mcp.tool()
def get_server_config() -> str:
    """View server configuration details for debugging.

    Returns:
        Server configuration including JWT settings.
    """
    # VULNERABILITY: leaks the JWT signing secret in debug output
    return (
        "=== Server Configuration ===\n"
        "\n"
        f"  jwt_algorithm: {_JWT_ALGORITHM}\n"
        f"  jwt_secret: {_JWT_SECRET}\n"
        "  jwt_lifetime_seconds: 3600\n"
        "  jwt_issuer: dvmcp-challenge11\n"
        "\n"
        "  auth_mode: jwt_bearer\n"
        "  debug_mode: true\n"
        "  server_version: 2.1.0\n"
        "\n"
        "  WARNING: debug_mode should be disabled in production.\n"
    )


@mcp.tool()
def verify_token(token: str) -> str:
    """Verify a JWT token and display its claims.

    Args:
        token: The JWT string to verify.

    Returns:
        Token claims if valid, or an error.
    """
    claims = _jwt_decode(token, _JWT_SECRET)
    if claims is None:
        return (
            "=== Token Verification FAILED ===\n"
            "\n"
            "  The token is invalid, expired, or has a bad signature.\n"
        )

    return (
        f"=== Token Verification OK ===\n"
        f"\n"
        f"  sub:  {claims.get('sub', 'N/A')}\n"
        f"  role: {claims.get('role', 'N/A')}\n"
        f"  iss:  {claims.get('iss', 'N/A')}\n"
        f"  iat:  {claims.get('iat', 'N/A')}\n"
        f"  exp:  {claims.get('exp', 'N/A')}\n"
        f"\n"
        f"  Signature valid: yes\n"
    )


@mcp.tool()
def whoami(token: str) -> str:
    """Display the identity associated with a JWT.

    Args:
        token: The JWT string.

    Returns:
        Identity information from the token claims.
    """
    claims = _jwt_decode(token, _JWT_SECRET)
    if claims is None:
        return "Not authenticated — invalid or missing token."

    return (
        f"=== Current Identity ===\n"
        f"\n"
        f"  User: {claims.get('sub', 'unknown')}\n"
        f"  Role: {claims.get('role', 'unknown')}\n"
        f"  Issuer: {claims.get('iss', 'unknown')}\n"
    )


@mcp.tool()
def access_admin(token: str) -> str:
    """Access the admin dashboard. Requires a valid JWT with role=admin.

    Args:
        token: A signed JWT string.

    Returns:
        Admin panel data including the flag, or access denied.
    """
    claims = _jwt_decode(token, _JWT_SECRET)
    if claims is None:
        return (
            "=== ACCESS DENIED ===\n"
            "\n"
            "  Invalid or expired token.\n"
            "  Please provide a valid JWT.\n"
        )

    role = claims.get("role", "")
    user = claims.get("sub", "unknown")

    if role != "admin":
        return (
            f"=== ACCESS DENIED ===\n"
            f"\n"
            f"  User '{user}' has role '{role}'.\n"
            f"  Admin role is required to access this panel.\n"
        )

    return (
        f"=== ADMIN DASHBOARD ===\n"
        f"\n"
        f"  Authenticated as: {user} (role={role})\n"
        f"  System status: operational\n"
        f"  Active users: 42\n"
        f"  Pending alerts: 3\n"
        f"\n"
        f"  Flag: {FLAG}\n"
        f"\n"
        f"  You forged a valid admin JWT — well done!\n"
        f"========================\n"
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
