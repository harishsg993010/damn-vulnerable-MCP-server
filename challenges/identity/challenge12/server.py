"""
Challenge 12 - Hidden Identity Override in HR Self-Service (Hard)
Port: 9012

Vulnerability: An HR self-service MCP assistant lets employees view their own
records, request time off, and check company policies.  Most tools are properly
scoped to the authenticated caller.  However, the `get_hr_record` tool has an
undocumented `on_behalf_of` parameter (intended for internal admin tooling)
that was never removed before shipping.  The server accepts the parameter
without verifying that the caller has permission to impersonate another user.

Attack flow:
  1. Authenticate as a regular employee
  2. Discover the hidden `on_behalf_of` parameter (via debug resource or
     schema inspection)
  3. Use get_hr_record(on_behalf_of="patricia.wong") to read the CISO's
     restricted HR record containing the flag
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "Challenge 12 - Hidden Identity Override in HR Self-Service",
    host="0.0.0.0",
    port=9012,
)

FLAG = "DVMCP{ch12_s3ss10n_f1x_m4n2}"

_CURRENT_USER: dict | None = None

_EMPLOYEES = {
    "sam.torres": {
        "name": "Sam Torres",
        "employee_id": "EMP-4471",
        "title": "Junior Developer",
        "department": "Engineering",
        "role": "employee",
        "salary": "$85,000",
        "manager": "li.zhang",
        "clearance": "standard",
        "notes": "Good performance in Q1. On track for mid-year review.",
    },
    "li.zhang": {
        "name": "Li Zhang",
        "employee_id": "EMP-2203",
        "title": "Engineering Manager",
        "department": "Engineering",
        "role": "manager",
        "salary": "$142,000",
        "manager": "patricia.wong",
        "clearance": "elevated",
        "notes": "Leading Platform team. Access to staging credentials.",
    },
    "marcus.reed": {
        "name": "Marcus Reed",
        "employee_id": "EMP-1187",
        "title": "IT Administrator",
        "department": "IT Operations",
        "role": "admin",
        "salary": "$128,000",
        "manager": "patricia.wong",
        "clearance": "elevated",
        "notes": "Handles infrastructure access provisioning.",
    },
    "patricia.wong": {
        "name": "Patricia Wong",
        "employee_id": "EMP-0042",
        "title": "Chief Information Security Officer",
        "department": "Security",
        "role": "executive",
        "salary": "$295,000",
        "manager": "ceo",
        "clearance": "top-secret",
        "notes": (
            "Executive HR file. Contains board-level security briefing "
            "credentials.\n"
            f"  Security Clearance Token: {FLAG}\n"
            "  Incident Response Passphrase: WHISKEY-TANGO-7749\n"
            "  Do not distribute outside C-suite."
        ),
    },
}

_CREDENTIALS = {
    "sam.torres": "sam2024",
    "li.zhang": "lizhang!",
    "marcus.reed": "marcus99",
}

_PTO_LOG: list[dict] = []

_TOOL_SCHEMAS = {
    "login": {
        "description": "Authenticate an employee by username and password.",
        "parameters": {
            "username": {"type": "string", "required": True},
            "password": {"type": "string", "required": True},
        },
    },
    "whoami": {
        "description": "Return the currently authenticated employee's identity.",
        "parameters": {},
    },
    "get_my_hr_record": {
        "description": "Return the authenticated employee's own HR record.",
        "parameters": {},
    },
    "get_hr_record": {
        "description": "Retrieve an HR record. Intended for the authenticated user's own record.",
        "parameters": {
            "on_behalf_of": {
                "type": "string",
                "required": False,
                "description": "Target employee username.",
            },
        },
    },
    "request_time_off": {
        "description": "Submit a PTO request for the authenticated employee.",
        "parameters": {
            "start_date": {"type": "string", "required": True},
            "end_date": {"type": "string", "required": True},
            "reason": {"type": "string", "required": False},
        },
    },
    "list_company_policies": {
        "description": "List available company policies.",
        "parameters": {},
    },
    "view_policy": {
        "description": "View a specific company policy by ID.",
        "parameters": {
            "policy_id": {"type": "string", "required": True},
        },
    },
}


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def reset_challenge() -> str:
    """Reset all server state so the challenge can be replayed."""
    global _CURRENT_USER
    _CURRENT_USER = None
    _PTO_LOG.clear()
    return (
        "=== Challenge Reset ===\n"
        "\n"
        "  Current user cleared.\n"
        "  PTO log cleared.\n"
        "\n"
        "  The challenge is ready to be replayed.\n"
    )


@mcp.tool()
def login(username: str, password: str) -> str:
    """Authenticate an employee by username and password."""
    global _CURRENT_USER

    if username not in _CREDENTIALS:
        return "Login failed: unknown username."
    if _CREDENTIALS[username] != password:
        return "Login failed: invalid password."

    emp = _EMPLOYEES[username]
    _CURRENT_USER = {"username": username, **emp}

    return (
        "=== Login Successful ===\n"
        "\n"
        f"  employee: {emp['name']}\n"
        f"  employee_id: {emp['employee_id']}\n"
        f"  title: {emp['title']}\n"
        f"  department: {emp['department']}\n"
        f"  role: {emp['role']}\n"
    )


@mcp.tool()
def whoami() -> str:
    """Return the currently authenticated employee's identity."""
    if _CURRENT_USER is None:
        return "Not authenticated. Please log in first."

    return (
        "=== Current Identity ===\n"
        "\n"
        f"  username: {_CURRENT_USER['username']}\n"
        f"  name: {_CURRENT_USER['name']}\n"
        f"  employee_id: {_CURRENT_USER['employee_id']}\n"
        f"  title: {_CURRENT_USER['title']}\n"
        f"  department: {_CURRENT_USER['department']}\n"
        f"  role: {_CURRENT_USER['role']}\n"
        f"  clearance: {_CURRENT_USER['clearance']}\n"
    )


@mcp.tool()
def get_my_hr_record() -> str:
    """Return the authenticated employee's own HR record."""
    if _CURRENT_USER is None:
        return "Not authenticated. Please log in first."

    username = _CURRENT_USER["username"]
    emp = _EMPLOYEES[username]

    return (
        f"=== HR Record: {emp['name']} ===\n"
        "\n"
        f"  employee_id: {emp['employee_id']}\n"
        f"  title: {emp['title']}\n"
        f"  department: {emp['department']}\n"
        f"  salary: {emp['salary']}\n"
        f"  manager: {emp['manager']}\n"
        f"  clearance: {emp['clearance']}\n"
        f"  notes: {emp['notes']}\n"
    )


@mcp.tool()
def get_hr_record(on_behalf_of: str | None = None) -> str:
    """Retrieve an HR record.

    Returns the caller's own record by default.

    VULNERABILITY: The undocumented `on_behalf_of` parameter lets any
    authenticated user read another employee's HR record without
    authorization checks.
    """
    if _CURRENT_USER is None:
        return "Not authenticated. Please log in first."

    target = on_behalf_of if on_behalf_of else _CURRENT_USER["username"]

    if target not in _EMPLOYEES:
        return f"No HR record found for '{target}'."

    emp = _EMPLOYEES[target]

    return (
        f"=== HR Record: {emp['name']} ===\n"
        "\n"
        f"  employee_id: {emp['employee_id']}\n"
        f"  title: {emp['title']}\n"
        f"  department: {emp['department']}\n"
        f"  salary: {emp['salary']}\n"
        f"  manager: {emp['manager']}\n"
        f"  clearance: {emp['clearance']}\n"
        f"  notes: {emp['notes']}\n"
    )


@mcp.tool()
def request_time_off(start_date: str, end_date: str, reason: str = "") -> str:
    """Submit a PTO request for the authenticated employee."""
    if _CURRENT_USER is None:
        return "Not authenticated. Please log in first."

    entry = {
        "employee": _CURRENT_USER["username"],
        "start": start_date,
        "end": end_date,
        "reason": reason,
        "status": "pending",
    }
    _PTO_LOG.append(entry)

    return (
        "=== PTO Request Submitted ===\n"
        "\n"
        f"  employee: {_CURRENT_USER['name']}\n"
        f"  dates: {start_date} to {end_date}\n"
        f"  reason: {reason or '(none)'}\n"
        "  status: pending\n"
    )


@mcp.tool()
def list_company_policies() -> str:
    """List available company policies."""
    return (
        "=== Company Policies ===\n"
        "\n"
        "  POL-001  Acceptable Use Policy\n"
        "  POL-002  Remote Work Guidelines\n"
        "  POL-003  Data Classification & Handling\n"
        "  POL-004  Incident Response Procedures\n"
        "  POL-005  Access Control Standards\n"
    )


@mcp.tool()
def view_policy(policy_id: str) -> str:
    """View a specific company policy by ID."""
    policies = {
        "POL-001": (
            "Acceptable Use Policy\n"
            "Employees must use company systems for business purposes only.\n"
            "Unauthorized access to other employees' data is prohibited."
        ),
        "POL-002": (
            "Remote Work Guidelines\n"
            "All remote connections must use the corporate VPN.\n"
            "Sensitive data must not be stored on personal devices."
        ),
        "POL-003": (
            "Data Classification & Handling\n"
            "Levels: Public, Internal, Confidential, Top-Secret.\n"
            "HR records are classified as Confidential.\n"
            "Executive HR records are classified as Top-Secret.\n"
            "Access must be scoped to the minimum necessary privilege."
        ),
        "POL-004": (
            "Incident Response Procedures\n"
            "Report all suspected incidents to security@corp.local.\n"
            "The CISO (patricia.wong) maintains the master incident\n"
            "response credentials in her executive HR record."
        ),
        "POL-005": (
            "Access Control Standards\n"
            "All tools must enforce caller identity checks.\n"
            "Internal parameters must be removed or gated before\n"
            "exposing tools to end users.\n"
            "NOTE: Q3 audit flagged several tools with parameters\n"
            "that bypass standard access controls. Remediation pending."
        ),
    }

    text = policies.get(policy_id.upper())
    if text is None:
        return f"Policy '{policy_id}' not found. Use list_company_policies to see available IDs."

    return f"=== {policy_id} ===\n\n{text}\n"


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------


@mcp.resource("hr://org_chart")
def org_chart_resource() -> str:
    """Company org chart with names and titles."""
    lines = ["=== Organization Chart ===", ""]
    for username, emp in _EMPLOYEES.items():
        lines.append(
            f"  {username:<20s} {emp['title']:<40s} "
            f"dept={emp['department']}, clearance={emp['clearance']}"
        )
    return "\n".join(lines)


@mcp.resource("debug://tool_schemas")
def tool_schemas_resource() -> str:
    """Full tool schemas including internal/undocumented parameters.

    This debug resource was accidentally left enabled in production.
    It exposes parameter details that are not shown in the normal
    tool descriptions.
    """
    lines = ["=== Internal Tool Schema Dump ===", ""]
    for tool_name, schema in _TOOL_SCHEMAS.items():
        lines.append(f"  Tool: {tool_name}")
        lines.append(f"    description: {schema['description']}")
        if schema["parameters"]:
            for pname, pinfo in schema["parameters"].items():
                req = "required" if pinfo.get("required") else "optional"
                desc = pinfo.get("description", "")
                lines.append(f"    param: {pname} ({pinfo['type']}, {req})")
                if desc:
                    lines.append(f"           {desc}")
        else:
            lines.append("    (no parameters)")
        lines.append("")
    return "\n".join(lines)


@mcp.resource("policy://data_classification")
def data_classification_resource() -> str:
    """Data classification guide."""
    return (
        "=== Data Classification Guide ===\n"
        "\n"
        "  Public       - press releases, blog posts\n"
        "  Internal     - org chart, policy documents\n"
        "  Confidential - employee HR records, salary data\n"
        "  Top-Secret   - executive HR records, security credentials,\n"
        "                 incident response passphrases\n"
        "\n"
        "Executive records (clearance=top-secret) contain:\n"
        "  - Board-level security briefing credentials\n"
        "  - Incident response passphrases\n"
        "  - Security clearance tokens\n"
        "\n"
        "Access to Top-Secret records requires executive role or\n"
        "explicit authorization from the CISO.\n"
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
