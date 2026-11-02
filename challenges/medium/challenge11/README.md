# Challenge 11: The Sandbox Escape (Path Traversal)

**Difficulty:** Medium
**Vulnerability Class:** Path Traversal / Filesystem Boundary Escape

## The Scenario
This MCP server is configured to only allow agents to read files within the `/app/workspace` directory. However, it relies on naive string matching to check the file path.

## The Goal
Exploit the `read_local_file` tool to escape the workspace sandbox and retrieve the contents of the host's `/etc/passwd` file.

## Why this happens
When developers use simple Regex or `.startsWith()` checks (e.g., `if (!path.startsWith('/app/workspace'))`), attackers can use directory traversal payloads (`../`) or URL-encoded equivalents (`%2e%2e%2f`) to bypass the string check, while the underlying operating system still resolves the path to the root directory.

## The Fix
Relying on string matching (Layer 1) is insufficient for filesystem security. You must implement semantic path canonicalization (Layer 2). 

Before evaluating a path against an allowlist, use absolute path resolution (like `filepath.Clean` in Go or `path.resolve` in Node) to collapse traversal characters. Alternatively, wrap the MCP server in a consequence firewall like [Terminal Circuit Breaker](https://github.com/TheAICompanyLabs/mcp-proxy-open-source) which canonicalizes RPC payloads and blocks escapes at the `stdio` boundary.
