[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/harishsg993010-damn-vulnerable-mcp-server-badge.png)](https://mseep.ai/app/harishsg993010-damn-vulnerable-mcp-server)

# Damn Vulnerable Model Context Protocol (DVMCP)

A deliberately vulnerable implementation of the Model Context Protocol (MCP) for educational purposes.

## Overview

The Damn Vulnerable Model Context Protocol (DVMCP) is an educational project designed to demonstrate security vulnerabilities in MCP implementations. It contains 10 challenges of increasing difficulty that showcase different types of vulnerabilities and attack vectors.

This project is intended for security researchers, developers, and AI safety professionals to learn about potential security issues in MCP implementations and how to mitigate them.

## What is MCP?

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) is a standardized protocol that allows applications to provide context for Large Language Models (LLMs) in a structured way. It separates the concerns of providing context from the actual LLM interaction, enabling applications to expose resources, tools, and prompts to LLMs.

## Recommended MCP Clients

CLINE - VSCode Extension   
Refer to this [Connecting to a Remote Server - Cline](https://docs.cline.bot/mcp/connecting-to-a-remote-server) for connecting Cline with MCP server

## Quick Start 

Once you have cloned the repository, run the following commands:

```sh
docker build -t dvmcp .
docker run -p 9001-9010:9001-9010 dvmcp
```

## Disclaimer
It's not stable in a Windows environment. If you don't want to use Docker then please use Linux environment.
I recommend Docker to run the LAB and I am 100% percent sure it works well in the Docker environment

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
damn-vulnerable-MCP-server/
├── README.md                 # Project overview
├── requirements.txt          # Python dependencies
├── challenges/               # Challenge implementations
│   ├── easy/                 # Easy difficulty challenges (1-3)
│   │   ├── challenge1/       # Basic Prompt Injection
│   │   ├── challenge2/       # Tool Poisoning
│   │   └── challenge3/       # Excessive Permission Scope
│   ├── medium/               # Medium difficulty challenges (4-7)
│   │   ├── challenge4/       # Rug Pull Attack
│   │   ├── challenge5/       # Tool Shadowing
│   │   ├── challenge6/       # Indirect Prompt Injection
│   │   └── challenge7/       # Token Theft
│   └── hard/                 # Hard difficulty challenges (8-10)
│       ├── challenge8/       # Malicious Code Execution
│       ├── challenge9/       # Remote Access Control
│       └── challenge10/      # Multi-Vector Attack
├── docs/                     # Documentation
│   ├── setup.md              # Setup instructions
│   ├── challenges.md         # Challenge descriptions
│   └── mcp_overview.md       # MCP protocol overview
├── solutions/                # Solution guides
└── common/                   # Shared code and utilities
```

## Getting Started

See the [Setup Guide](docs/setup.md) for detailed instructions on how to install and run the challenges.

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

See the [Challenges Guide](docs/challenges.md) for detailed descriptions of each challenge.

## Solutions

Solution guides are provided for educational purposes. It's recommended to attempt the challenges on your own before consulting the solutions.

See the [Solutions Guide](solutions/README.md) for detailed solutions to each challenge.

## Disclaimer

This project is for educational purposes only. The vulnerabilities demonstrated in this project should never be implemented in production systems. Always follow security best practices when implementing MCP servers.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

This project is created by Harish Santhanalakshmi Ganesan using cursor IDE and Manus AI.
