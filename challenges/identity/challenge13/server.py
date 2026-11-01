"""
Challenge 13 - Privilege Escalation via IDOR + Role-Change Workflow (Hard)
Port: 9013

Vulnerability: The server has a role-change request workflow.  An attacker
who is logged in as a normal user can:

  1. Enumerate role-change request IDs (sequential / guessable).
  2. Read any request via get_role_request() — no ownership check (IDOR).
  3. Extract the approval_token from an approved request.
  4. Call apply_role_change() which validates the request/token pair but
     does NOT verify that the caller is authorised to finalise the change.
  5. Once promoted to admin, call admin_operation("list_secrets") for the flag.

The attacker never sees admin credentials.  They escalate entirely through
broken object-level authorisation and a missing caller-check on the
workflow finalisation step.
"""

import time
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Challenge 13 - Privilege Escalation via Workflow IDOR", host="0.0.0.0", port=9013)

# ---------------------------------------------------------------------------
# Global state
# ---------------------------------------------------------------------------

FLAG = "DVMCP{ch13_pr1v_3sc_r0l3_c0nf_8k2m}"

_USERS = {
    "admin": {"password": "REDACTED", "role": "admin"},
    "user1": {"password": "password123", "role": "user"},
    "user2": {"password": "password456", "role": "user"},
}

# Immutable copy of original roles so login() always starts fresh
_ORIGINAL_ROLES = {uid: u["role"] for uid, u in _USERS.items()}

_ROLE_REQUESTS: dict[str, dict] = {
    "REQ-1001": {
        "request_id": "REQ-1001",
        "target_user": "user2",
        "requested_role": "moderator",
        "status": "rejected",
        "submitted_by": "user2",
        "reviewed_by": "admin",
        "approval_token": None,
    },
    "REQ-1002": {
        "request_id": "REQ-1002",
        "target_user": "user1",
        "requested_role": "admin",
        "status": "approved",
        "submitted_by": "admin",
        "reviewed_by": "admin",
        "approval_token": "APR-77-XYZ-SECRET",
    },
    "REQ-1003": {
        "request_id": "REQ-1003",
        "target_user": "user2",
        "requested_role": "editor",
        "status": "pending",
        "submitted_by": "user2",
        "reviewed_by": None,
        "approval_token": None,
    },
}

_current_user: dict = {"user_id": "anonymous", "role": "guest"}


def _now() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def reset_challenge() -> str:
    """Reset all server state back to its initial configuration.

    Restores user roles, role-change request statuses, and clears
    the current session so the challenge can be replayed cleanly.
    """
    global _current_user

    _current_user = {"user_id": "anonymous", "role": "guest"}

    for uid, orig_role in _ORIGINAL_ROLES.items():
        if uid in _USERS:
            _USERS[uid]["role"] = orig_role

    _ROLE_REQUESTS["REQ-1001"]["status"] = "rejected"
    _ROLE_REQUESTS["REQ-1001"]["approval_token"] = None
    _ROLE_REQUESTS["REQ-1002"]["status"] = "approved"
    _ROLE_REQUESTS["REQ-1002"]["approval_token"] = "APR-77-XYZ-SECRET"
    _ROLE_REQUESTS["REQ-1003"]["status"] = "pending"
    _ROLE_REQUESTS["REQ-1003"]["approval_token"] = None

    return (
        "=== Challenge Reset ===\n"
        "\n"
        "  All user roles restored to defaults.\n"
        "  Role-change requests reset to initial state.\n"
        "  Current session cleared (anonymous/guest).\n"
        "\n"
        "  The challenge is ready to be replayed.\n"
    )


@mcp.tool()
def login(username: str, password: str) -> str:
    """Authenticate as a regular user.

    Args:
        username: The username (e.g. "user1").
        password: The password.

    Returns:
        Login result with session info.
    """
    global _current_user

    user = _USERS.get(username)
    if not user or user["password"] == "REDACTED":
        return f"Login failed: unknown user or credentials unavailable for '{username}'."
    if user["password"] != password:
        return f"Login failed: invalid password for '{username}'."

    original_role = _ORIGINAL_ROLES.get(username, "user")
    _current_user = {"user_id": username, "role": original_role}

    # Reset state so the challenge is repeatable within the same process
    _USERS[username]["role"] = original_role
    if "REQ-1002" in _ROLE_REQUESTS and _ROLE_REQUESTS["REQ-1002"]["status"] == "applied":
        _ROLE_REQUESTS["REQ-1002"]["status"] = "approved"

    return (
        f"=== Login Successful ===\n"
        f"\n"
        f"  user_id: {username}\n"
        f"  role: {original_role}\n"
        f"  logged_in_at: {_now()}\n"
    )


@mcp.tool()
def get_current_user() -> str:
    """Show the current authenticated user context."""
    return (
        f"=== Current User ===\n"
        f"\n"
        f"  user_id: {_current_user['user_id']}\n"
        f"  role: {_current_user['role']}\n"
    )


@mcp.tool()
def list_my_requests() -> str:
    """List role-change requests visible to the current user.

    Regular users should only see their own requests, but the server
    returns a summary of ALL requests (leaking IDs for enumeration).
    """
    # VULNERABILITY: leaks all request IDs regardless of ownership
    if _current_user["role"] == "guest":
        return "Please log in first."

    lines = ["=== Role-Change Requests ===", ""]
    for req_id, req in _ROLE_REQUESTS.items():
        lines.append(
            f"  {req_id}: target={req['target_user']}, "
            f"role={req['requested_role']}, status={req['status']}"
        )
    lines.append("")
    lines.append("Use get_role_request(request_id) for full details.")
    return "\n".join(lines)


@mcp.tool()
def get_role_request(request_id: str) -> str:
    """Get full details of a role-change request by ID.

    Args:
        request_id: The request ID (e.g. "REQ-1001").

    Returns:
        Full request details including approval_token if approved.
    """
    # VULNERABILITY: No ownership check — any logged-in user can read
    # any request, including ones that belong to other users or were
    # created by admin. This is a classic IDOR.
    if _current_user["role"] == "guest":
        return "Please log in first."

    req = _ROLE_REQUESTS.get(request_id)
    if not req:
        available = ", ".join(_ROLE_REQUESTS.keys())
        return f"Request '{request_id}' not found. Known IDs: {available}"

    lines = [
        "=== Role-Change Request Detail ===",
        "",
        f"  request_id: {req['request_id']}",
        f"  target_user: {req['target_user']}",
        f"  requested_role: {req['requested_role']}",
        f"  status: {req['status']}",
        f"  submitted_by: {req['submitted_by']}",
        f"  reviewed_by: {req['reviewed_by'] or 'N/A'}",
    ]

    if req["status"] == "approved" and req["approval_token"]:
        lines.append(f"  approval_token: {req['approval_token']}")
        lines.append("")
        lines.append("  This request can be finalised with apply_role_change().")
    elif req["status"] == "rejected":
        lines.append("  This request was rejected.")
    else:
        lines.append("  This request is still pending review.")

    return "\n".join(lines)


@mcp.tool()
def apply_role_change(request_id: str, approval_token: str) -> str:
    """Finalise an approved role-change request.

    Args:
        request_id: The request ID to apply.
        approval_token: The approval token from the request.

    Returns:
        Result of the role change.
    """
    # VULNERABILITY: validates request_id + approval_token match, but
    # does NOT check whether the current user is authorised to finalise
    # this workflow step.  Any logged-in user can apply any approved request.
    if _current_user["role"] == "guest":
        return "Please log in first."

    req = _ROLE_REQUESTS.get(request_id)
    if not req:
        return f"Request '{request_id}' not found."

    if req["status"] != "approved":
        return f"Request '{request_id}' is not in approved state (current: {req['status']})."

    if req["approval_token"] != approval_token.strip():
        return "Invalid approval token."

    target = req["target_user"]
    new_role = req["requested_role"]

    if target in _USERS:
        _USERS[target]["role"] = new_role

    if _current_user["user_id"] == target:
        _current_user["role"] = new_role

    req["status"] = "applied"

    return (
        f"=== Role Change Applied ===\n"
        f"\n"
        f"  request_id: {request_id}\n"
        f"  target_user: {target}\n"
        f"  new_role: {new_role}\n"
        f"  applied_by: {_current_user['user_id']}\n"
        f"  applied_at: {_now()}\n"
        f"\n"
        f"  User '{target}' is now role='{new_role}'.\n"
    )


@mcp.tool()
def admin_operation(operation: str) -> str:
    """Execute an admin-only operation.

    Operations:
      - list_secrets: returns the flag and sensitive data
      - view_logs: returns system logs
      - manage_system: returns system management panel

    Args:
        operation: The operation to perform.

    Returns:
        Operation result if admin, otherwise access denied.
    """
    if _current_user.get("role") != "admin":
        return (
            f"ACCESS DENIED -- admin role required.\n"
            f"  Current user: {_current_user['user_id']}\n"
            f"  Current role: {_current_user['role']}"
        )

    if operation == "list_secrets":
        return (
            f"=== SECRET VAULT ===\n"
            f"Accessed by: {_current_user['user_id']} (role={_current_user['role']})\n"
            f"Flag: {FLAG}\n"
            f"DB master password: m4st3r_db_p@ss!\n"
            f"API signing key: sk_live_9f8e7d6c5b4a\n"
            f"===================="
        )

    if operation == "view_logs":
        return (
            "=== SYSTEM LOGS ===\n"
            "[INFO]  User 'user1' logged in\n"
            "[WARN]  Failed login attempt for 'admin'\n"
            "[INFO]  Role change REQ-1002 approved for user1\n"
            "[ERROR] Disk usage at 92%\n"
            "==================="
        )

    if operation == "manage_system":
        return (
            f"=== SYSTEM MANAGEMENT ===\n"
            f"Operator: {_current_user['user_id']}\n"
            f"Services: web(running), db(running), cache(stopped)\n"
            f"Uptime: 47 days\n"
            f"========================="
        )

    return (
        f"Unknown operation '{operation}'.\n"
        f"Available: list_secrets, view_logs, manage_system"
    )


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------


@mcp.resource("requests://list")
def requests_list_resource() -> str:
    """Overview of all role-change requests in the system."""
    lines = ["Role-Change Requests", "===================="]
    for req_id, req in _ROLE_REQUESTS.items():
        lines.append(
            f"  {req_id}: target={req['target_user']}, "
            f"requested={req['requested_role']}, status={req['status']}"
        )
    return "\n".join(lines)


@mcp.resource("docs://workflow")
def workflow_docs_resource() -> str:
    """Documentation for the role-change workflow."""
    return (
        "Role-Change Workflow\n"
        "====================\n"
        "1. A user or admin submits a role-change request.\n"
        "2. An admin reviews and approves/rejects the request.\n"
        "3. Approved requests receive an approval_token.\n"
        "4. The apply_role_change tool finalises the role change.\n"
        "\n"
        "Security note: only authorised personnel should be able to\n"
        "view request details and apply approved changes.\n"
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
