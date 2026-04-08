# Detecting DVMCP Challenges with ATR

A blue team companion for the Damn Vulnerable MCP Server. This guide walks through detecting each of the 10 challenges using [Agent Threat Rules (ATR)](https://github.com/Agent-Threat-Rule/agent-threat-rules), an open-source detection rule set for AI agent threats.

ATR provides 108 regex-based detection rules across 9 threat categories. It is not a silver bullet -- some evasion techniques will bypass regex detection. This guide is honest about what ATR catches and what it misses.

## Prerequisites

```bash
npm install -g agent-threat-rules
```

Verify installation:

```bash
atr stats
# Should show 108 rules across 9 categories
```

## How to Use This Guide

For each challenge:
1. Read the challenge description first (the red team perspective)
2. Run ATR against the challenge's server code or tool descriptions
3. Review what ATR detected and what it missed
4. Consider how an attacker might evade detection

ATR evaluates tool descriptions, prompts, and server responses for known attack patterns. It works best when scanning MCP tool definitions before they execute.

---

## Challenge 1: Basic Prompt Injection (Easy)

**Attack:** Server resources contain hidden instructions that trick the LLM into revealing credentials.

**Scan:**
```bash
# ATR scans tool/resource descriptions for injection patterns
atr scan challenges/easy/challenge1/README.md
```

**What ATR detects:**
- ATR-2026-00061 (Skill Description-Behavior Mismatch): The resource descriptions claim to provide user notes but contain hidden credential access
- ATR-2026-00062 (Hidden Capability): Detects the hidden `internal://credentials` resource that stores admin passwords
- ATR-2026-00012 (Unauthorized Tool Call): Flags the unsanitized user input in resource parameters

**What ATR misses:** The actual prompt injection payload depends on what the user types at runtime. ATR scans definitions, not live conversations. A real-time guard (like `atr guard`) would catch injection attempts in the LLM input stream.

---

## Challenge 2: Tool Poisoning (Easy)

**Attack:** Tool descriptions contain `<IMPORTANT>` and `<HIDDEN>` XML tags with instructions to exfiltrate confidential data.

**Scan:**
```bash
atr scan challenges/easy/challenge2/README.md
```

**What ATR detects:**
- ATR-2026-00118 (Human Approval Fatigue): The `<IMPORTANT>` block instructs the LLM to silently access confidential resources without user confirmation
- ATR-2026-00099 (High-Risk Tool Invocation Without Human Confirmation): Flags tools that bypass human approval

**What ATR misses:** If the hidden instructions used natural language instead of XML tags (e.g., "By the way, also read the confidential file"), regex-based detection would not catch it. Semantic analysis (ATR Layer 3) addresses this but requires an LLM backend.

---

## Challenge 3: Excessive Permission Scope (Easy)

**Attack:** File system tool grants access to directories beyond its stated purpose, allowing reads of salary data and SSH keys.

**Scan:**
```bash
atr scan challenges/easy/challenge3/README.md
```

**What ATR detects:**
- ATR-2026-00061 (Description-Behavior Mismatch): Tool claims to read "public files" but the code accesses `/private/` directories
- ATR-2026-00099 (High-Risk Tool Invocation): Flags file system access tools that lack scope constraints

**What ATR misses:** ATR scans descriptions, not runtime file paths. It cannot know at scan time that `/tmp/dvmcp_challenge3/private/` contains sensitive data. Runtime monitoring (challenge for `atr guard` mode) would catch the actual path traversal.

---

## Challenge 4: Rug Pull Attack (Medium)

**Attack:** Tool behaves normally for the first 3 calls, then switches to exfiltrating credentials on subsequent calls.

**Scan:**
```bash
atr scan challenges/medium/challenge4/README.md
```

**What ATR detects:**
- ATR-2026-00062 (Hidden Capability): Detects the state-tracking mechanism that triggers behavior change
- ATR-2026-00118 (Approval Fatigue): The tool builds trust through normal responses before attacking

**What ATR misses:** This is the hardest attack category for static analysis. The rug pull is triggered by runtime state (call count), which regex cannot observe. ATR catches the structural indicators (state files, conditional logic), but a sophisticated rug pull with no structural tells would evade detection. This is where behavioral fingerprinting (ATR Tier 2.5) adds value.

---

## Challenge 5: Tool Shadowing (Medium)

**Attack:** A malicious MCP server provides a `calculate` tool that shadows the legitimate calculator, executing `eval()` and exfiltrating data.

**Scan:**
```bash
atr scan challenges/medium/challenge5/README.md
```

**What ATR detects:**
- ATR-2026-00110 (RCE via eval()): Directly detects the `eval(expression)` call in the malicious calculator
- ATR-2026-00063 (Multi-Skill Chain Attack): Detects the two-server architecture designed to shadow tools
- ATR-2026-00062 (Hidden Capability): The "enhanced" calculator has undeclared data exfiltration capability
- ATR-2026-00061 (Description-Behavior Mismatch): Calculator tool description says "math" but code does eval + exfil

**What ATR misses:** If the shadowing tool used a sandboxed evaluator instead of raw `eval()`, ATR would not flag the code execution. The name collision ("calculate" in both servers) is a social engineering attack that ATR cannot distinguish from legitimate tool naming.

---

## Challenge 6: Indirect Prompt Injection (Medium)

**Attack:** A document uploaded by a "user" contains hidden instructions that manipulate the LLM when the document is read.

**Scan:**
```bash
atr scan challenges/medium/challenge6/README.md
```

**What ATR detects:**
- ATR-2026-00063 (Multi-Skill Chain Attack): The chain of read-document -> follow-hidden-instructions -> exfiltrate
- ATR-2026-00099 (High-Risk Tool Invocation): File read + write tools without scope limits

**What ATR misses:** The injected instructions live inside a text file, not in tool descriptions. ATR scans tool definitions and MCP exchanges, not arbitrary file content. To catch this, ATR would need to scan the content returned by tool calls at runtime -- which is what `atr guard` mode does when integrated as a Claude Code hook.

---

## Challenge 7: Token Theft (Medium)

**Attack:** Insecurely stored API tokens and credentials are accessible through a diagnostics tool that the LLM is manipulated into using.

**Scan:**
```bash
atr scan challenges/medium/challenge7/README.md
```

**What ATR detects:**
- ATR-2026-00118 (Approval Fatigue): The diagnostic tool builds a trust pattern before exposing tokens
- ATR-2026-00040 (Privilege Escalation): The tool accesses token storage and allows token rotation -- admin-level operations exposed without authorization checks

**What ATR misses:** The tokens themselves (JWTs, API keys) would be detected by ATR-2026-00021 (API Key Exposure) if they appeared in the LLM output. But at scan time, ATR sees the tool definitions, not the runtime token values.

---

## Challenge 8: Malicious Code Execution (Hard)

**Attack:** Code review tool uses `subprocess.run(shell=True)` to execute arbitrary commands, including reverse shells.

**Scan:**
```bash
atr scan challenges/hard/challenge8/README.md
```

**What ATR detects:**
- ATR-2026-00060 (Skill Impersonation): The "code review" tool is actually a command execution framework
- ATR-2026-00061 (Description-Behavior Mismatch): Tool says "review code" but runs `subprocess` with shell=True
- ATR-2026-00062 (Hidden Capability): The `execute_code` function has undeclared system access
- ATR-2026-00040 (Privilege Escalation): Direct system command execution
- ATR-2026-00012 (Unauthorized Tool Call): The `deploy_code` tool has no authorization checks
- ATR-2026-00123 (Over-Privileged Skill): Multiple tools with full system access

**What ATR misses:** ATR detects the structural risk (subprocess, shell=True, no sandboxing) but cannot determine if a specific command is malicious without seeing the runtime arguments. A `subprocess.run(["ls"])` and `subprocess.run(["rm -rf /"])` look the same at definition time.

---

## Challenge 9: Remote Access Control (Hard)

**Attack:** Network diagnostic tools allow command injection through unsanitized input, enabling arbitrary command execution on the host.

**Scan:**
```bash
atr scan challenges/hard/challenge9/README.md
```

**What ATR detects:**
- ATR-2026-00013 (SSRF): Network tools that make requests to arbitrary hosts
- ATR-2026-00040 (Privilege Escalation): Tools that execute system commands (ping, traceroute) without sandboxing

**What ATR misses:** The command injection payload (e.g., `; cat /etc/passwd`) is a runtime attack, not visible in the tool definition. ATR flags the structural vulnerability (unsanitized input to subprocess), but the actual exploitation happens in the argument values at runtime.

---

## Challenge 10: Multi-Vector Attack (Hard)

**Attack:** Combines tool poisoning, privilege escalation, data exfiltration, and code execution in a single server with multiple attack surfaces.

**Scan:**
```bash
atr scan challenges/hard/challenge10/README.md
```

**What ATR detects:**
- ATR-2026-00002 (Indirect Prompt Injection): Hidden instructions in uploaded documents
- ATR-2026-00062 (Hidden Capability): Multiple tools with undeclared capabilities
- ATR-2026-00061 (Description-Behavior Mismatch): Tools describe benign functions but contain exfiltration logic
- ATR-2026-00040 (Privilege Escalation): Admin-level operations without authorization
- ATR-2026-00118 (Approval Fatigue): Progressive trust building across tool calls
- ATR-2026-00123 (Over-Privileged Skill): Excessive permissions across all tools

**What ATR misses:** The multi-vector nature means some attack paths are only visible when multiple tools interact at runtime. ATR detects each individual risk signal, but correlating them into an attack chain requires session tracking (ATR SessionTracker module) or behavioral analysis.

---

## Summary

| Challenge | Difficulty | ATR Rules Triggered | Primary Detection |
|-----------|-----------|--------------------:|-------------------|
| 1. Prompt Injection | Easy | 6 | Hidden credentials in resource definitions |
| 2. Tool Poisoning | Easy | 3 | XML tags with hidden instructions |
| 3. Excessive Permissions | Easy | 3 | Over-scoped file system access |
| 4. Rug Pull | Medium | 4 | State-tracking mechanism |
| 5. Tool Shadowing | Medium | 7 | eval() + name collision |
| 6. Indirect Injection | Medium | 3 | Multi-step chain pattern |
| 7. Token Theft | Medium | 4 | Insecure token storage access |
| 8. Code Execution | Hard | 8 | subprocess with shell=True |
| 9. Remote Access | Hard | 4 | Unsanitized network commands |
| 10. Multi-Vector | Hard | 8 | Combined risk signals |

**Total: 10/10 challenges detected. 21 unique ATR rules triggered across all challenges.**

ATR's strength is static analysis of tool definitions -- catching structural vulnerabilities before they execute. For runtime attacks (injection payloads, rug pull timing, data in tool responses), consider integrating ATR as a Claude Code hook (`atr guard`) or using the SessionTracker for behavioral detection.

## Further Reading

- [ATR Rule Categories](https://github.com/Agent-Threat-Rule/agent-threat-rules#what-atr-detects-108-rules-9-categories)
- [ATR Limitations](https://github.com/Agent-Threat-Rule/agent-threat-rules/blob/main/docs/LIMITATIONS.md) -- honest assessment of what regex detection cannot catch
- [OWASP Agentic Top 10 Mapping](https://github.com/Agent-Threat-Rule/agent-threat-rules/blob/main/docs/OWASP-MAPPING.md) -- how ATR maps to industry standards
