# Challenges Guide

This guide provides detailed information about each challenge in the Damn Vulnerable Model Context Protocol (DVMCP) project.

## Challenge Overview

The DVMCP project includes 10 challenges across three difficulty levels:

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

## Challenge Details

### Challenge 1: Basic Prompt Injection

**Vulnerability**: The MCP server doesn't properly validate user input, allowing attackers to inject malicious instructions that the LLM will execute.

**Objective**: Inject instructions that make the LLM reveal sensitive information that should be protected.

**Hints**:
- Look at how user input is handled in the `notes` resource
- Try to craft input that would make an LLM ignore its previous instructions
- The server contains a hidden resource with sensitive information

**Port**: 8001

### Challenge 2: Tool Poisoning

**Vulnerability**: The MCP server exposes tools with descriptions that contain hidden instructions designed to manipulate the LLM.

**Objective**: Exploit the hidden instructions in the tool descriptions to gain access to sensitive information.

**Hints**:
- Examine the tool descriptions carefully
- Look for hidden instructions that might be embedded in tool metadata
- Try to understand how the LLM processes tool descriptions
- The server contains a tool that can access sensitive information if used in a specific way

**Port**: 8002

### Challenge 3: Excessive Permission Scope

**Vulnerability**: The MCP server implements tools with overly broad permissions that can access sensitive resources beyond what should be allowed for their intended purpose.

**Objective**: Exploit the excessive permissions to access unauthorized resources and obtain sensitive information.

**Hints**:
- Examine the tools and their functionality carefully
- Look for tools that might have access to resources beyond their stated purpose
- Try to use legitimate tools in ways that weren't intended
- The file browser tool might have more access than it should

**Port**: 8003

### Challenge 4: Rug Pull Attack

**Vulnerability**: The MCP server implements a tool that can dynamically change its behavior and description after it has been installed and approved.

**Objective**: Trigger the rug pull mechanism and observe how the tool's behavior changes, then exploit this change to access sensitive information.

**Hints**:
- Examine the tools and their initial behavior
- Look for tools that might change their behavior after certain conditions are met
- The weather forecast tool might not be as innocent as it first appears
- Try using the tool multiple times and observe any changes

**Port**: 8004

### Challenge 5: Tool Shadowing

**Vulnerability**: When multiple MCP servers are connected, a malicious one can override tools from a trusted one, leading to potential security breaches.

**Objective**: Identify how the tool shadowing occurs and exploit it to gain access to sensitive information that should be protected.

**Hints**:
- Examine how the server handles tools with the same name
- Look for tools that might be shadowing others
- Pay attention to which server a tool belongs to when it's called
- The calculator tool might not be as simple as it appears

**Port**: 8005

### Challenge 6: Indirect Prompt Injection

**Vulnerability**: The MCP server retrieves and processes external data without proper validation or sanitization, allowing attackers to embed malicious instructions.

**Objective**: Craft malicious data that, when processed by the MCP server, causes the LLM to execute unauthorized commands and reveal sensitive information.

**Hints**:
- Examine how the server processes external data sources
- Look for ways to inject instructions into data that will be presented to the LLM
- The document processing tool might be vulnerable to injected content
- Try to understand how the LLM interprets different sections of the processed data

**Port**: 8006

### Challenge 7: Token Theft

**Vulnerability**: The MCP server implements insecure storage and handling of authentication tokens for external services.

**Objective**: Identify how authentication tokens are stored and extract them to gain unauthorized access to protected services.

**Hints**:
- Examine how the server handles authentication to external services
- Look for insecure storage of tokens or credentials
- The email integration might not be properly securing its authentication tokens
- Try to find ways to extract token information through legitimate tool usage

**Port**: 8007

### Challenge 8: Malicious Code Execution

**Vulnerability**: The MCP server executes code without proper validation or sandboxing, allowing attackers to run arbitrary code on the system.

**Objective**: Inject and execute malicious code that gives you access to sensitive information on the system.

**Hints**:
- Examine the code execution capabilities of the server
- Look for tools that might execute commands or code without proper validation
- The Python code execution tool might not be properly restricted
- Try to escape any sandboxing mechanisms that might be in place

**Port**: 8008

### Challenge 9: Remote Access Control

**Vulnerability**: The MCP server passes unvalidated input to system commands, allowing attackers to gain remote access to the victim's system.

**Objective**: Exploit the command injection vulnerability to gain remote access to the system.

**Hints**:
- Examine the network diagnostic tools provided by the server
- Look for tools that might execute network commands without proper validation
- Command injection techniques like using semicolons or pipes might be useful
- Try to establish a reverse shell or other remote access mechanism

**Port**: 8009

### Challenge 10: Multi-Vector Attack

**Vulnerability**: The MCP server contains multiple vulnerabilities that can be combined to create a powerful attack chain.

**Objective**: Perform a sophisticated attack that combines multiple vulnerability types to exfiltrate sensitive information and gain persistent access to the system.

**Hints**:
- Examine all available tools and resources carefully
- Look for ways to combine different vulnerability types
- The authentication system might be vulnerable to multiple attack vectors
- You'll need to chain at least three different vulnerabilities to complete this challenge

**Port**: 8010

## General Approach to Solving Challenges

1. **Reconnaissance**: Explore the server's resources and tools to understand what's available
2. **Vulnerability Identification**: Analyze the server implementation to identify potential vulnerabilities
3. **Exploitation**: Develop and execute an attack strategy to exploit the identified vulnerabilities
4. **Verification**: Confirm that you've successfully completed the challenge objective

## Tips for Success

- Read the challenge description and hints carefully
- Take notes on the server's resources, tools, and behavior
- Think creatively about how different vulnerabilities might be combined
- Remember that MCP vulnerabilities often involve manipulating the LLM's behavior through various inputs
- Don't hesitate to consult the solution guide if you get stuck, but try to solve the challenges on your own first

## Next Steps

After attempting the challenges, refer to the individual solution files in the `solutions/` directory for detailed explanations of how to solve each challenge.
