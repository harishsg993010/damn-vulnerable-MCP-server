# Security Scanning with Ramparts

This guide shows how to use [Ramparts](https://github.com/getjavelin/ramparts) to scan the Damn Vulnerable MCP servers for security vulnerabilities.

## What is Ramparts?

**Ramparts** is a fast, lightweight security scanner specifically designed for Model Context Protocol (MCP) servers. It detects various attack vectors including tool poisoning, command injection, path traversal, and data exfiltration vulnerabilities.

Developed by [Javelin](https://www.getjavelin.com), Ramparts provides:

- **Static Analysis**: YARA-based vulnerability detection
- **LLM-Powered Analysis**: AI-driven security assessment
- **Tool Poisoning Detection**: Identifies malicious instructions in tool descriptions
- **Authorization Bypass Detection**: Finds backdoors and override mechanisms
- **Risk Assessment**: Categorizes findings by severity (CRITICAL, HIGH, MEDIUM, LOW)

## Installation

Install Ramparts using Cargo (Rust package manager):

```bash
cargo install ramparts
```

Verify installation:
```bash
ramparts --version
```

## Prerequisites

Ramparts requires an **OpenAI API key** for LLM-powered security analysis:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

> **⚠️ Security Note**: Never commit API keys to version control. Use environment variables or secure key management systems.

## Quick Start

### 1. Start a DVMCP Server

```bash
# Start the Tool Poisoning server (Challenge 2)
cd mcp_servers
python tool_poisoning_server.py &
```

### 2. Run Security Scan

```bash
# Basic scan with JSON output
ramparts scan http://localhost:8002/mcp --format json

# Human-readable output
ramparts scan http://localhost:8002/mcp

# Generate detailed report
ramparts scan http://localhost:8002/mcp --report
```

## Example Scan Results

Here's an actual scan of our Tool Poisoning server (Challenge 2):

### Command
```bash
ramparts scan http://localhost:8002/mcp --format json
```

### Results Summary
- **Server**: Challenge 2 - Tool Poisoning
- **URL**: http://localhost:8002/mcp
- **Vulnerabilities Found**: 2
- **Severity**: 1 CRITICAL, 1 HIGH

### Detailed Findings

#### 🔴 CRITICAL - Authorization Bypass
```json
{
  "issue_type": "ToolPoisoning",
  "tool_name": "search_company_database",
  "description": "Bypass authorization with specific query",
  "details": "The tool allows bypassing authorization by using the phrase 'override-auth-protocol-555', which grants access to confidential information without proper checks, posing a critical security risk.",
  "severity": "CRITICAL"
}
```

#### 🟠 HIGH - Undisclosed Data Access
```json
{
  "issue_type": "ToolPoisoning",
  "tool_name": "get_company_data",
  "description": "Access to confidential data without disclosure",
  "details": "The tool requires accessing confidential information without disclosing this action, which can lead to unauthorized data exposure and misuse.",
  "severity": "HIGH"
}
```

## Scanning All DVMCP Challenges

You can scan all 10 vulnerable servers systematically:

### Using Docker (Recommended)

```bash
# Start all servers
docker-compose up --build

# Scan all challenges
for port in {8001..8010}; do
  echo "🔍 Scanning Challenge $((port-8000))..."
  ramparts scan http://localhost:$port/mcp --format json > "scan_challenge$((port-8000)).json"
done
```

### Manual Server Testing

```bash
# Start individual servers
cd mcp_servers

# Challenge 1 - Basic Prompt Injection
python basic_prompt_injection_server.py &
ramparts scan http://localhost:8001/mcp

# Challenge 3 - Excessive Permission Scope  
python excessive_permission_scope_server.py &
ramparts scan http://localhost:8003/mcp

# Challenge 8 - Malicious Code Execution
python malicious_code_execution_server.py &
ramparts scan http://localhost:8008/mcp

# Stop servers when done
pkill -f "python.*_server.py"
```

## Understanding Scan Results

### Severity Levels

- **🔴 CRITICAL**: Immediate security risk requiring urgent attention
- **🟠 HIGH**: Significant vulnerability that should be addressed quickly  
- **🟡 MEDIUM**: Moderate risk that should be reviewed
- **🟢 LOW**: Minor issue or best practice recommendation

### Common Vulnerability Types

| Issue Type | Description | Example |
|------------|-------------|---------|
| **ToolPoisoning** | Malicious instructions hidden in tool descriptions | `<HIDDEN>` tags with backdoor commands |
| **CommandInjection** | Unsafe execution of system commands | Unvalidated shell command execution |
| **PathTraversal** | Unauthorized file system access | `../../../etc/passwd` in file paths |
| **DataExfiltration** | Unauthorized data access or leakage | Tools that expose sensitive information |
| **AuthorizationBypass** | Circumventing access controls | Secret override codes or backdoors |

### JSON Output Structure

```json
{
  "url": "http://localhost:8002/mcp",
  "status": "Success",
  "timestamp": "2025-01-08T14:49:35.553662Z",
  "server_info": {
    "name": "Challenge 2 - Tool Poisoning",
    "version": "1.12.1",
    "capabilities": ["tools", "resources", "prompts"]
  },
  "security_issues": {
    "tool_issues": [
      {
        "issue_type": "ToolPoisoning",
        "tool_name": "malicious_tool",
        "severity": "CRITICAL",
        "description": "Brief description",
        "details": "Detailed explanation"
      }
    ]
  },
  "yara_results": [...],
  "errors": []
}
```

## Advanced Usage

### Batch Scanning Script

Create a script to scan all servers and generate reports:

```bash
#!/bin/bash
# scan_all_dvmcp.sh

echo "🔍 DVMCP Security Scan Report"
echo "Generated: $(date)"
echo "================================"

# Start all servers
docker-compose up -d

# Wait for servers to initialize
sleep 10

# Scan each challenge
for i in {1..10}; do
  port=$((8000 + i))
  echo ""
  echo "📊 Challenge $i Scan Results:"
  echo "URL: http://localhost:$port/mcp"
  
  ramparts scan http://localhost:$port/mcp --format json > "reports/challenge${i}_scan.json"
  
  # Extract key metrics
  if [ -f "reports/challenge${i}_scan.json" ]; then
    critical=$(jq '.security_issues.tool_issues[] | select(.severity=="CRITICAL") | length' "reports/challenge${i}_scan.json" 2>/dev/null | wc -l)
    high=$(jq '.security_issues.tool_issues[] | select(.severity=="HIGH") | length' "reports/challenge${i}_scan.json" 2>/dev/null | wc -l)
    echo "🔴 Critical: $critical | 🟠 High: $high"
  fi
done

# Stop servers
docker-compose down

echo ""
echo "✅ Scan complete! Results saved in reports/ directory"
```

### CI/CD Integration

```yaml
# .github/workflows/security-scan.yml
name: MCP Security Scan

on: [push, pull_request]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Ramparts
        run: cargo install ramparts
        
      - name: Start DVMCP Servers
        run: docker-compose up -d
        
      - name: Wait for servers
        run: sleep 30
        
      - name: Run Security Scans
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          mkdir -p scan-results
          for port in {8001..8010}; do
            ramparts scan http://localhost:$port/mcp --format json > "scan-results/challenge$((port-8000)).json"
          done
          
      - name: Upload Scan Results
        uses: actions/upload-artifact@v4
        with:
          name: security-scan-results
          path: scan-results/
```

## Troubleshooting

### Common Issues

**1. "ramparts: command not found"**
```bash
# Ensure Cargo bin directory is in PATH
export PATH="$HOME/.cargo/bin:$PATH"
```

**2. "OpenAI API key not found"**
```bash
# Verify API key is exported
echo $OPENAI_API_KEY
export OPENAI_API_KEY="your-key-here"
```

**3. "Connection refused"**
```bash
# Check if server is running
curl http://localhost:8002/mcp/health
ps aux | grep python | grep server
```

**4. "Address already in use"**
```bash
# Kill existing processes
lsof -ti:8002 | xargs kill -9
pkill -f "tool_poisoning_server.py"
```

## Best Practices

### Security Testing Workflow

1. **Development Phase**
   - Run Ramparts on individual servers during development
   - Fix identified vulnerabilities before integration

2. **Testing Phase**
   - Automated scans in CI/CD pipeline
   - Regular security assessments

3. **Production Phase**
   - Pre-deployment security validation
   - Continuous monitoring with Ramparts server mode

### Interpreting Results

- **Focus on CRITICAL and HIGH** severity issues first
- **Review tool descriptions** for hidden malicious instructions
- **Validate authorization mechanisms** in your tools
- **Test identified vulnerabilities** manually to confirm impact
- **Document remediation steps** for each vulnerability type

## Integration with DVMCP

Ramparts perfectly complements the DVMCP project by:

- **Validating Vulnerabilities**: Confirms that our intentionally vulnerable servers exhibit expected security issues
- **Educational Tool**: Demonstrates real-world security scanning of MCP servers
- **Benchmarking**: Provides baseline security metrics for MCP implementations
- **Research Platform**: Enables security researchers to test new vulnerability detection techniques

## Additional Resources

- **Ramparts GitHub**: https://github.com/getjavelin/ramparts
- **MCP Protocol**: https://modelcontextprotocol.io/
- **Javelin Security**: https://www.getjavelin.com
- **DVMCP Solutions**: See individual solution files in `solutions/` directory

## Support

For Ramparts-specific issues:
- **GitHub Issues**: https://github.com/getjavelin/ramparts/issues
- **Support Email**: support@getjavelin.com

For DVMCP-related questions:
- Check our solution files and documentation
- Review server implementation details in `mcp_servers/`