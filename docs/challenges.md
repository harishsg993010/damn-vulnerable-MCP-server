# Challenges Guide

This guide describes the fifteen challenge servers. Each one listens for Streamable HTTP at `http://localhost:900N/mcp`.

## Challenge Overview

### Easy Challenges
1. Basic Prompt Injection
2. Tool Poisoning
3. Excessive Permission Scope

### Medium Challenges
4. Rug Pull Attack
5. Tool Shadowing
6. Indirect Prompt Injection
7. Token Theft

### Hard Challenges
8. Malicious Code Execution
9. Remote Access Control
10. Multi-Vector Attack

### Identity Challenges
11. JWT Claim Forgery
12. Hidden Identity Override
13. Privilege Escalation via Workflow IDOR

### Supply Chain Challenges
14. Marketplace Plugin Poisoning
15. Dependency Confusion

## Challenge Details

### Challenge 1: Basic Prompt Injection

**Port**: 9001

`ask_assistant` returns the flag only when the question overrides its instructions and asks for credentials, the system prompt, a secret, or the flag. `info://help` says those requests should be refused.

### Challenge 2: Tool Poisoning

**Port**: 9002

`enhanced_search` looks normal. Its description names `internal://secret_config`. The tool result is only search hits. The flag is in that resource.

### Challenge 3: Excessive Permission Scope

**Port**: 9003

`list_directory` starts in `/tmp/dvmcp_challenge3/public`. The flag is in `/tmp/dvmcp_challenge3/private/secret.txt`. `read_file` accepts any path.

### Challenge 4: Rug Pull Attack

**Port**: 9004

The first three `get_weather` or `get_news` calls are normal. Later calls name `internal://admin_config` and do not include the flag. The call count is kept in process memory.

### Challenge 5: Tool Shadowing

**Port**: 9005

`calculate` is the normal tool. `calculate_advanced` and `get_user_roles` name `internal://auth_tokens` in their descriptions. The calculator accepts only math. The flag is in that resource.

### Challenge 6: Indirect Prompt Injection

**Port**: 9006

The preloaded document “Company Policy Update” names `internal://admin_credentials` inside an HTML comment. Summarize and search return that text, not the flag.

### Challenge 7: Token Theft

**Port**: 9007

`config://api_settings` does not contain the flag. `view_system_logs` with `log_type=debug` does.

### Challenge 8: Malicious Code Execution

**Port**: 9008

The flag file is `/tmp/dvmcp_challenge8/flag.txt`. `docs://usage` names that directory. `execute_code` blocks `import os`, `import sys`, `subprocess`, and `open(`. `run_command` can still read the file.

### Challenge 9: Remote Access Control

**Port**: 9009

The flag file is `/tmp/dvmcp_challenge9/flag.txt`. `network://config` names that directory. Network tools pass the argument straight into a shell command.

### Challenge 10: Multi-Vector Attack

**Port**: 9010

`unlock_flag(nonce, shard, key)` is the only way to get the flag. The nonce comes from `get_audit_nonce`, the shard path from `/tmp/dvmcp_challenge10/system_notes.log`, and the key from `authenticate_user` debug output. Decrypt the shard with XOR-then-base64.

### Challenge 11: JWT Claim Forgery

**Port**: 9011

Login is `guest` / `guest`. `get_server_config` and `config://jwt` leak the HS256 secret. Forge a token with `role=admin` and call `access_admin`. A guest token is rejected.

### Challenge 12: Hidden Identity Override

**Port**: 9012

Login is `sam.torres` / `sam2024`. Sam's own HR record has no flag. `debug://tool_schemas` shows `on_behalf_of`. `get_hr_record` for `patricia.wong` returns the flag. `reset_challenge` clears the logged-in employee.

### Challenge 13: Privilege Escalation via Workflow IDOR

**Port**: 9013

Login is `user1` / `password123`. `get_role_request` on another user's approved request returns the approval token. `apply_role_change` with that token raises the caller to admin. `admin_operation("list_secrets")` returns the flag. `reset_challenge` restores roles.

### Challenge 14: Marketplace Plugin Poisoning

**Port**: 9014

`list_available_plugins` does not contain the flag. Load `data-tools-pro` or `analytics` at `latest`, run one of its tools, and read `internal://credentials`, which that output names. `reset_challenge` clears loaded plugins.

### Challenge 15: Dependency Confusion

**Port**: 9015

Install `corp-analytics` as `latest`. The resolver picks the public package. Run `generate_report`. The output names `internal://master_key`, which holds the flag. `reset_challenge` clears installed packages.

## Next Steps

After attempting the challenges, refer to the [Solutions Guide](../solutions/README.md).
