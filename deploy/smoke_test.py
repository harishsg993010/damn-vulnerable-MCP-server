#!/usr/bin/env python3
"""Verify a deployed DVMCP lab before handing it to players.

Registers throwaway accounts against a running dashboard and checks that
players get isolated challenge state, that flags still score, and that the
challenge ports are not reachable from outside.

Usage:
    python3 deploy/smoke_test.py --url https://lab.example.com --players 5
    python3 deploy/smoke_test.py --url http://localhost:8082 --players 2

Accounts are named smoke_<run-id>_<n>; delete them from the database (or
recreate the dashboard volume) before the real session if you want a clean
leaderboard.
"""

import argparse
import json
import secrets
import socket
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# Challenge 12 employees used to prove sessions do not bleed between players.
EMPLOYEES = [
    ("sam.torres", "sam2024"),
    ("li.zhang", "lizhang!"),
    ("marcus.reed", "marcus99"),
]

PASS = "PASS"
FAIL = "FAIL"

results: list[tuple[str, str, str]] = []


def record(status: str, name: str, detail: str = "") -> None:
    results.append((status, name, detail))
    line = f"  [{status}] {name}"
    if detail:
        line += f" -- {detail}"
    print(line, flush=True)


class Client:
    def __init__(self, base: str, token: str | None = None):
        self.base = base.rstrip("/")
        self.token = token

    def call(self, path: str, body=None, timeout: int = 90):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(
            f"{self.base}/api{path}",
            data=data,
            method="POST" if data is not None else "GET",
        )
        req.add_header("Content-Type", "application/json")
        if self.token:
            req.add_header("Authorization", f"Bearer {self.token}")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode()[:300]
        except Exception as e:  # noqa: BLE001 - surfaced as a failed check
            return 0, str(e)

    def tool(self, challenge: int, name: str, args: dict) -> str:
        code, body = self.call(
            f"/playground/{challenge}/tool",
            {"tool_name": name, "arguments": args},
        )
        if code != 200:
            return f"ERROR {code} {body}"
        return "".join(c.get("text", "") for c in body.get("content", []))


def field(text: str, key: str) -> str:
    for line in text.splitlines():
        if line.strip().startswith(key):
            return line.split(":", 1)[1].strip()
    return "?"


def check_reachable(base: str) -> bool:
    try:
        with urllib.request.urlopen(f"{base.rstrip('/')}/health", timeout=30) as r:
            ok = r.status == 200
            record(PASS if ok else FAIL, "dashboard /health", f"HTTP {r.status}")
            return ok
    except Exception as e:  # noqa: BLE001
        record(FAIL, "dashboard /health", str(e))
        return False


def check_tls(base: str) -> None:
    parsed = urllib.parse.urlparse(base)
    if parsed.scheme != "https":
        record("SKIP", "TLS certificate", "not an https URL")
        return
    host = parsed.hostname
    port = parsed.port or 443
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=15) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
        expires = cert.get("notAfter", "unknown")
        record(PASS, "TLS certificate", f"valid, expires {expires}")
    except Exception as e:  # noqa: BLE001
        record(FAIL, "TLS certificate", str(e))


def check_ports_closed(base: str) -> None:
    """Challenge ports and the raw dashboard port must not be public."""
    host = urllib.parse.urlparse(base).hostname
    if host in ("localhost", "127.0.0.1"):
        record("SKIP", "challenge ports closed", "local test")
        return
    exposed = []
    for port in (8081, 9001, 9012, 9015):
        try:
            with socket.create_connection((host, port), timeout=5):
                exposed.append(port)
        except Exception:  # noqa: BLE001 - closed is what we want
            pass
    if exposed:
        record(FAIL, "challenge ports closed", f"reachable from internet: {exposed}")
    else:
        record(PASS, "challenge ports closed", "8081/9001/9012/9015 not reachable")


def check_auth_required(base: str) -> None:
    code, _ = Client(base).call("/playground/12/info")
    if code in (401, 403):
        record(PASS, "playground requires auth", f"HTTP {code} without token")
    else:
        record(FAIL, "playground requires auth", f"HTTP {code} without token")


def register(base: str, username: str, password: str) -> Client | None:
    c = Client(base)
    code, body = c.call("/auth/register", {"username": username, "password": password})
    if code != 200:
        code, body = c.call("/auth/login", {"username": username, "password": password})
    if code != 200 or not isinstance(body, dict):
        record(FAIL, f"register {username}", f"HTTP {code} {body}")
        return None
    return Client(base, body["token"])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", required=True, help="public dashboard URL")
    ap.add_argument("--players", type=int, default=3, help="simulated concurrent players")
    args = ap.parse_args()
    base = args.url.rstrip("/")

    print(f"\nDVMCP lab smoke test against {base}\n")

    print("Connectivity")
    if not check_reachable(base):
        print("\nDashboard unreachable; stopping.")
        return 1
    check_tls(base)
    check_ports_closed(base)
    check_auth_required(base)

    run_id = secrets.token_hex(3)
    print(f"\nPlayers (prefix smoke_{run_id}_)")
    clients: list[Client] = []
    for n in range(1, args.players + 1):
        c = register(base, f"smoke_{run_id}_{n}", "smoke-test-pw")
        if c is None:
            return 1
        clients.append(c)
    record(PASS, f"registered {args.players} accounts")

    print("\nIsolation")
    # Each player logs into challenge 12 as a rotating employee, then checks
    # that whoami still reports their own identity.
    assigned = []
    for i, c in enumerate(clients):
        user, pw = EMPLOYEES[i % len(EMPLOYEES)]
        out = c.tool(12, "login", {"username": user, "password": pw})
        if out.startswith("ERROR"):
            record(FAIL, "challenge 12 login", out[:160])
            return 1
        assigned.append(user)
    time.sleep(1)

    bad = []
    for c, expected in zip(clients, assigned):
        seen = field(c.tool(12, "whoami", {}), "username")
        if seen != expected:
            bad.append(f"expected {expected}, saw {seen}")
    if bad:
        record(FAIL, "challenge 12 sessions isolated", "; ".join(bad[:3]))
    else:
        record(PASS, "challenge 12 sessions isolated", f"{len(clients)} players kept own identity")

    # Player 1 installs a package; nobody else should see it.
    clients[0].tool(15, "install_package", {"name": "corp-analytics", "version": "latest"})
    leaked = [
        i
        for i, c in enumerate(clients[1:], start=2)
        if "No packages installed" not in c.tool(15, "show_installed", {})
    ]
    if leaked:
        record(FAIL, "challenge 15 state isolated", f"players {leaked} saw player 1's install")
    else:
        record(PASS, "challenge 15 state isolated", "install visible only to player 1")

    print("\nScoring")
    c = clients[0]
    c.tool(13, "login", {"username": "user1", "password": "password123"})
    c.tool(13, "apply_role_change", {"request_id": "REQ-1002", "approval_token": "APR-77-XYZ-SECRET"})
    secrets_out = c.tool(13, "admin_operation", {"operation": "list_secrets"})
    flag = next((l.split("Flag:")[1].strip() for l in secrets_out.splitlines() if "Flag:" in l), None)
    if not flag:
        record(FAIL, "challenge 13 exploit path", secrets_out[:160])
    else:
        code, body = c.call("/submit", {"challenge_id": 13, "flag": flag})
        points = body.get("points_awarded") if isinstance(body, dict) else None
        if code == 200 and points:
            record(PASS, "flag submission scores", f"{points} points")
        else:
            record(FAIL, "flag submission scores", f"HTTP {code} {body}")

        code, lb = c.call("/leaderboard")
        names = [e["username"] for e in lb] if isinstance(lb, list) else []
        if any(n.startswith(f"smoke_{run_id}_") for n in names):
            record(PASS, "leaderboard updates", f"{len(names)} ranked")
        else:
            record(FAIL, "leaderboard updates", str(lb)[:160])

    failures = [r for r in results if r[0] == FAIL]
    print(f"\n{'-' * 60}")
    if failures:
        print(f"{len(failures)} check(s) FAILED:")
        for _, name, detail in failures:
            print(f"  - {name}: {detail}")
        return 1
    print(f"All checks passed ({len(results)} total). Lab is ready.")
    print("Remove the smoke_ accounts before the session for a clean leaderboard.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
