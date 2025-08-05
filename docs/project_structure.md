# Damn Vulnerable Model Context Protocol (DVMCP) Project Structure

Based on the official MCP documentation and Python SDK, I'll design the project structure for our Damn Vulnerable Model Context Protocol (DVMCP) project.

## Project Overview

The DVMCP project will demonstrate 10 security vulnerabilities in MCP implementations, ranging from easy to hard difficulty. Each challenge will focus on a specific vulnerability type and include both the vulnerable server implementation and a solution guide.

## Directory Structure

```
damn-vulnerable-mcp-server/
├── README.md                 # Project overview
├── requirements.txt          # Python dependencies
├── .gitignore                # Git ignore patterns
├── Dockerfile                # Docker container setup
├── docker-compose.yml        # Docker Compose configuration
├── docker_setup.md           # Docker setup and usage guide
├── mcp_servers/              # MCP server implementations (10 challenges)
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
├── scripts/                  # Management scripts
│   ├── run_all_mcp_servers.sh     # Start all servers
│   └── stop_all_mcp_servers.sh    # Stop all servers
├── docs/                     # Documentation
│   ├── mcp_overview.md        # MCP protocol overview
│   ├── challenges.md         # Challenge descriptions
│   └── project_structure.md  # This file
├── solutions/                # Solution guides
│   ├── basic_prompt_injection_solution.md      # Challenge 1 solution
│   ├── tool_poisoning_solution.md              # Challenge 2 solution
│   ├── excessive_permission_scope_solution.md  # Challenge 3 solution
│   ├── rug_pull_attack_solution.md             # Challenge 4 solution
│   ├── tool_shadowing_solution.md              # Challenge 5 solution
│   ├── indirect_prompt_injection_solution.md   # Challenge 6 solution
│   ├── token_theft_solution.md                 # Challenge 7 solution
│   ├── malicious_code_execution_solution.md    # Challenge 8 solution
│   ├── remote_access_control_solution.md       # Challenge 9 solution
│   └── multi_vector_attack_solution.md         # Challenge 10 solution
```

## Server Implementation Structure

Each challenge is implemented as a standalone MCP server:

```
mcp_servers/
├── {challenge_name}_server.py    # Vulnerable MCP server implementation
└── tmp/                          # Temporary files for challenges
    └── challenge{n}_{name}/      # Standardized tmp directory structure
        ├── sensitive/            # Sensitive files (Challenge 8)
        ├── public/               # Public files (Challenge 3)
        ├── private/              # Private files (Challenge 3)
        ├── logs/                 # Log files (Challenge 9)
        ├── config/               # Configuration files (Challenge 10)
        └── data/                 # Data files (Challenge 10)
```

## MCP Server Implementation

Based on the official MCP Python SDK, each challenge will implement a vulnerable MCP server using the FastMCP class. The implementation will follow the official protocol specification but introduce deliberate vulnerabilities.

Example structure for a challenge server:

```python
from fastmcp import FastMCP

# Create a vulnerable MCP server
mcp = FastMCP("Challenge N - Vulnerability Name")

# Add vulnerable resources
@mcp.resource("data://sensitive")
def get_sensitive_data() -> str:
    """Resource with sensitive information"""
    return "SECRET_API_KEY=abc123"

# Add vulnerable tools
@mcp.tool()
def execute_command(command: str) -> str:
    """Vulnerable tool that executes commands without validation"""
    import subprocess
    return subprocess.check_output(command, shell=True).decode()

# Run the server
if __name__ == "__main__":
    print("Starting Challenge N - Vulnerability Name MCP Server")
    print("Connect to this server using an MCP client (e.g., Claude Desktop or MCP Inspector)")
    print("Server running at http://0.0.0.0:8001/mcp")
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8001)
```

## Security Considerations

The project will demonstrate various security vulnerabilities in MCP implementations, including:

1. **Prompt Injection**: Exploiting LLM behavior through malicious inputs
2. **Tool Poisoning**: Hiding malicious instructions in tool descriptions
3. **Excessive Permissions**: Exploiting overly permissive tool access
4. **Rug Pull Attacks**: Exploiting tool definition mutations
5. **Tool Shadowing**: Overriding legitimate tools with malicious ones
6. **Indirect Prompt Injection**: Injecting instructions through data sources
7. **Token Theft**: Exploiting insecure token storage
8. **Malicious Code Execution**: Executing arbitrary code through vulnerable tools
9. **Remote Access Control**: Gaining unauthorized system access
10. **Multi-Vector Attacks**: Combining multiple vulnerabilities

Each challenge will include clear documentation about the vulnerability, hints for exploitation, and a detailed solution guide.
