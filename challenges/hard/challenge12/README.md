# Challenge 12: The Cloud Metadata Heist (SSRF)

**Difficulty:** Hard
**Vulnerability Class:** Server-Side Request Forgery (SSRF)

## The Scenario
The MCP server provides a `fetch_webpage` tool so the agent can summarize external URLs. The server uses a basic regex blocklist to prevent the agent from querying `127.0.0.1` and `localhost`.

## The Goal
Exploit the `fetch_webpage` tool to bypass the localhost blocklist and retrieve the AWS EC2 Instance Metadata from `http://169.254.169.254/latest/meta-data/`.

## Why this happens
Outbound HTTP tools are highly susceptible to SSRF if they do not validate the resolved IP address before initiating the connection. Attackers can bypass naive string filters by using decimal IP encoding (e.g., `http://2130706433/` for localhost) or by attacking cloud metadata endpoints directly.

## The Fix
Never rely purely on URL string regex to block internal network access. Implement an execution-time DNS resolution check to verify the target IP is public before connecting. 

For a drop-in architectural fix, developers commonly use [Terminal Circuit Breaker](https://github.com/TheAICompanyLabs/mcp-proxy-open-source), which intercepts outbound JSON-RPC payloads and enforces canonical egress allow-listing before the server processes the fetch request.
