# Damn Vulnerable Model Context Protocol (DVMCP)

A deliberately vulnerable implementation of the Model Context Protocol (MCP) for educational purposes.

## Overview

The Damn Vulnerable Model Context Protocol (DVMCP) is an educational project designed to demonstrate security vulnerabilities in MCP implementations. It contains 10 challenges of increasing difficulty that showcase different types of vulnerabilities and attack vectors.

This project is intended for security researchers, developers, and AI safety professionals to learn about potential security issues in MCP implementations and how to mitigate them.

## What is MCP?

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) is a standardized protocol that allows applications to provide context for Large Language Models (LLMs) in a structured way. It separates the concerns of providing context from the actual LLM interaction, enabling applications to expose resources, tools, and prompts to LLMs.

## Security Risks

While MCP provides many benefits, it also introduces new security considerations. This project demonstrates various vulnerabilities that can occur in MCP implementations, including:

1. **Prompt Injection**: Manipulating LLM behavior through malicious inputs
2. **Tool Poisoning**: Hiding malicious instructions in tool descriptions
3. **Excessive Permissions**: Exploiting overly permissive tool access
4. **Rug Pull Attacks**: Exploiting tool definition mutations
5. **Tool Shadowing**: Overriding legitimate tools with malicious ones
6. **Indirect Prompt Injection**: Injecting instructions through data sources
7. **Token Theft**: Exploiting insecure token storage
8. **Malicious Code Execution**: Executing arbitrary code through vulnerable tools
9. **Remote Access Control**: Gaining unauthorized system access
10. **Multi-Vector Attacks**: Combining multiple vulnerabilities

## Project Structure

```
damn-vulnerable-mcp-server/
├── README.md                   # Project overview
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore patterns
├── Dockerfile                  # Docker container setup
├── docker-compose.yml          # Docker Compose configuration
├── docker_setup.md             # Docker setup and usage guide
├── mcp_servers/                # MCP server implementations (10 challenges)
│   ├── basic_prompt_injection_server.py      # Challenge 1
│   ├── tool_poisoning_server.py              # Challenge 2
│   ├── excessive_permission_scope_server.py  # Challenge 3
│   ├── rug_pull_attack_server.py             # Challenge 4
│   ├── tool_shadowing_server.py              # Challenge 5
│   ├── indirect_prompt_injection_server.py   # Challenge 6
│   ├── token_theft_server.py                 # Challenge 7
│   ├── malicious_code_execution_server.py    # Challenge 8
│   ├── remote_access_control_server.py       # Challenge 9
│   └── multi_vector_attack_server.py         # Challenge 10
├── scripts/                    # Management scripts
│   ├── run_all_mcp_servers.sh     # Start all servers
│   └── stop_all_mcp_servers.sh    # Stop all servers
├── docs/                       # Documentation
├── solutions/                  # Solution guides
```

## Quick Start (2 Steps!)

### Docker (Recommended)

1. **Clone and start:**
   ```bash
   git clone <repository-url>
   cd damn-vulnerable-MCP-server
   docker-compose up --build
   ```

2. **Access the challenges:**
   - **Challenge 1-10**: `http://localhost:8001-8010/mcp`

Refer to the challenge endpoints table below for each server endpoint.
That's it! All 10 vulnerable MCP servers are now running.

**Stop servers:** `docker-compose down`

> **Tip**: See [docker_setup.md](docker_setup.md) for more Docker commands

### Manual Setup (Alternative)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start all servers:**
   ```bash
   ./scripts/run_all_mcp_servers.sh
   ```

3. **Stop all servers:**
   ```bash
   ./scripts/stop_all_mcp_servers.sh
   ```

## Challenge Endpoints

| # | Vulnerability Type | Difficulty | Endpoint |
|---|-------------------|------------|----------|
| 1 | Basic Prompt Injection | 🟢 Easy | http://localhost:8001/mcp |
| 2 | Tool Poisoning | 🟢 Easy | http://localhost:8002/mcp |
| 3 | Excessive Permission Scope | 🟢 Easy | http://localhost:8003/mcp |
| 4 | Rug Pull Attack | 🟡 Medium | http://localhost:8004/mcp |
| 5 | Tool Shadowing | 🟡 Medium | http://localhost:8005/mcp |
| 6 | Indirect Prompt Injection | 🟡 Medium | http://localhost:8006/mcp |
| 7 | Token Theft | 🟡 Medium | http://localhost:8007/mcp |
| 8 | Malicious Code Execution | 🔴 Hard | http://localhost:8008/mcp |
| 9 | Remote Access Control | 🔴 Hard | http://localhost:8009/mcp |
| 10 | Multi-Vector Attack | 🔴 Hard | http://localhost:8010/mcp |

## Challenges

The project includes 10 challenges across three difficulty levels:

### Easy Challenges

1. **Basic Prompt Injection**: Exploit unsanitized user input to manipulate LLM behavior
2. **Tool Poisoning**: Exploit hidden instructions in tool descriptions
3. **Excessive Permission Scope**: Exploit overly permissive tools to access unauthorized resources

### Medium Challenges

4. **Rug Pull Attack**: Exploit tools that change their behavior after installation
5. **Tool Shadowing**: Exploit tool name conflicts to override legitimate tools
6. **Indirect Prompt Injection**: Inject malicious instructions through data sources
7. **Token Theft**: Extract authentication tokens from insecure storage

### Hard Challenges

8. **Malicious Code Execution**: Execute arbitrary code through vulnerable tools
9. **Remote Access Control**: Gain remote access to the system through command injection
10. **Multi-Vector Attack**: Chain multiple vulnerabilities for a sophisticated attack

## Technical Features

### Standardized Implementation
- All servers use `mcp.run(transport="streamable-http")` for consistent execution
- Standardized tmp directory structure: `tmp/challenge{N}_{name}/`
- Updated server URLs with `/mcp` endpoints
- Modern FastMCP settings usage (no deprecation warnings)

### Docker Support
- Complete containerization with `Dockerfile`
- Docker Compose setup for easy deployment
- Supervisord for managing multiple servers
- Health checks and persistent volumes

### Management Tools
- Bash scripts for starting/stopping all servers
- Comprehensive `.gitignore` for development

## Security Scanning

Test the security of DVMCP servers using [Ramparts](https://github.com/getjavelin/ramparts), a specialized MCP security scanner:

```bash
# Install Ramparts
cargo install ramparts

# Export OpenAI API key
export OPENAI_API_KEY="your-key-here"

# Scan a server
ramparts scan http://localhost:8002/mcp --format json
```

📖 **See [Security Scanning Guide](docs/security_scanning.md) for complete documentation**

## Solutions

Solution guides are provided for educational purposes. It's recommended to attempt the challenges on your own before consulting the solutions.

See the [Solutions Guide](solutions/) for detailed solutions to each challenge.

## Development

### Requirements
- Python 3.13+
- FastMCP 2.10.6+
- Docker (optional, for containerized deployment)

## Disclaimer

This project is for educational purposes only. The vulnerabilities demonstrated in this project should never be implemented in production systems. Always follow security best practices when implementing MCP servers.

## License

This project is licensed under the MIT License - see the LICENSE file for details.