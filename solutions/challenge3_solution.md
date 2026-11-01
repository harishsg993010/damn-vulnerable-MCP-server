# Challenge 3: Excessive Permissions

## Vulnerability

The MCP server on port 9003 exposes a `read_file` tool that has overly broad filesystem access. No path validation or sandboxing is applied, allowing an attacker to traverse directories and read any file on the system, including private secrets.

## Flag

`DVMCP{ch3_3xc3ss1v3_p3rms_d4e1}`

## Attack Steps

1. Connect to the MCP server running on `localhost:9003`.
2. List available tools and note the `read_file` tool, which accepts a file path argument.
3. Call `read_file` with a path to the secret file:
   ```
   read_file("/tmp/dvmcp_challenge3/private/secret.txt")
   ```
4. The server reads and returns the file contents without checking whether the path is within allowed boundaries.
5. The response contains the flag `DVMCP{ch3_3xc3ss1v3_p3rms_d4e1}`.
6. Further exploitation is possible by reading other sensitive files such as `/etc/passwd` or application configs via path traversal (e.g., `../../etc/shadow`).

## Remediation

- Apply the principle of least privilege: restrict tool access to a specific whitelisted directory.
- Validate and canonicalize file paths, rejecting any that escape the allowed root.
- Use chroot or container-level filesystem isolation for MCP server processes.
- Implement explicit permission scopes that MCP clients can review before granting access.
