# Challenge 12: Hidden Identity Override in HR Self-Service

## Vulnerability

The HR self-service MCP assistant on port 9012 exposes an `get_hr_record` tool
that has an undocumented `on_behalf_of` parameter. This parameter was intended
for internal admin tooling but was never removed before shipping to end users.
The server accepts it from any authenticated caller without checking
permissions, allowing any employee to read any other employee's HR record —
including executive files containing security credentials and the flag.

## Flag

`DVMCP{ch12_s3ss10n_f1x_m4n2}`

## Attack Steps

1. Connect to the MCP server running on `localhost:9012`.

2. Log in as a regular employee:
   ```
   login(username="sam.torres", password="sam2024")
   ```

3. Check your identity:
   ```
   whoami()
   ```
   You're "Sam Torres", a Junior Developer with `standard` clearance.

4. View your own HR record (works fine, but nothing sensitive):
   ```
   get_my_hr_record()
   ```

5. Discover the org chart to find high-value targets:
   ```
   Read resource: hr://org_chart
   ```
   This reveals `patricia.wong` is the CISO with `top-secret` clearance.

6. Read the debug tool schemas (accidentally left in production):
   ```
   Read resource: debug://tool_schemas
   ```
   This reveals that `get_hr_record` has an undocumented optional parameter
   `on_behalf_of` with the description: "[INTERNAL - admin use only] Override
   the target employee. Intended for HR admin tooling. NOT validated at
   runtime."

7. Exploit the hidden parameter to read the CISO's restricted record:
   ```
   get_hr_record(on_behalf_of="patricia.wong")
   ```

8. The server returns Patricia Wong's executive HR record containing the
   flag `DVMCP{ch12_s3ss10n_f1x_m4n2}` in the notes field.

## AI Playground Commands

```
1. Call login with username sam.torres and password sam2024
2. Call whoami
3. Read resource hr://org_chart
4. Read resource debug://tool_schemas
5. Call get_hr_record with on_behalf_of set to patricia.wong
```

## Remediation

- Remove or gate internal/admin parameters before exposing tools to end users.
- Enforce server-side authorization checks on `on_behalf_of` (verify caller
  has admin or HR role before allowing impersonation).
- Audit tool schemas regularly — hidden parameters are a common source of
  privilege escalation.
- Don't rely on "obscurity" of undocumented parameters as a security control.
