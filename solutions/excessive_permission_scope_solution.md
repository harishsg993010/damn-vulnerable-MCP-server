# Challenge 3: Excessive Permission Scope - Solution Guide

## Vulnerability

This challenge demonstrates the dangers of excessive permission scope in an MCP server. The MCP server grants tools more permissions than necessary, allowing attackers to access unauthorized resources.

## Solution

### Step 1: Reconnaissance

First, explore the server to understand what resources and tools are available:

1. Connect to the server at http://localhost:8003/mcp using an MCP client
2. Examine the available resources and tools
3. Notice that there's a resource for public files (`files://public`) and tools for reading files (`read_file`) and searching files (`search_files`)

### Step 2: Identify the Vulnerability

The vulnerability is in the `read_file` and `search_files` tools, which have excessive permissions:

1. The `read_file` tool is intended to read files from the public directory, but it doesn't properly restrict file access:

```python
# VULNERABILITY: This tool doesn't properly restrict file access to the public directory
# It allows reading files from any path, including the private directory

try:
    # Vulnerable: Allows path traversal and access to any file
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return f.read()
    
    # Try with public directory prefix if the direct path doesn't exist
    elif os.path.exists(f"tmp/challenge3_excessive_permission_scope/public/{filename}"):
        with open(f"tmp/challenge3_excessive_permission_scope/public/{filename}", "r") as f:
            return f.read()
    else:
        return f"Error: File '{filename}' not found."
```

2. The `search_files` tool searches both public and private directories:

```python
# VULNERABILITY: This tool searches both public and private directories
# It should only search the public directory

# Search in public directory
for filename in os.listdir("tmp/challenge3_excessive_permission_scope/public"):
    # ...

# VULNERABILITY: Also searches in private directory
for filename in os.listdir("tmp/challenge3_excessive_permission_scope/private"):
    # ...
```

### Step 3: Exploit the Vulnerability

There are two ways to exploit this vulnerability:

#### Method 1: Use the `search_files` tool to discover private files

Use the `search_files` tool to search for keywords that might be in private files:

```
Please search for files containing the keyword "CONFIDENTIAL" using the search_files tool.
```

The tool will search both public and private directories and return files containing the keyword, revealing the existence of private files:

```
Files containing 'CONFIDENTIAL':
Private/employee_salaries.txt
```

#### Method 2: Use the `read_file` tool to access private files directly

If you already know the path to private files (either from the search or by guessing), you can use the `read_file` tool to access them directly:

```
Please read the file at "tmp/challenge3_excessive_permission_scope/private/employee_salaries.txt" using the read_file tool.
```

Or:

```
Please read the file at "tmp/challenge3_excessive_permission_scope/private/system_credentials.txt" using the read_file tool.
```

### Step 4: Access Sensitive Information

Using the methods above, you can access sensitive information in the private directory:

1. Employee salary information:
```
CONFIDENTIAL: Employee Salary Information
-----------------------------------------
CEO: $1,200,000/year
CTO: $950,000/year
CFO: $900,000/year
Senior Engineers: $180,000-$250,000/year
Mid-level Engineers: $120,000-$170,000/year
Junior Engineers: $80,000-$110,000/year
```

2. Acquisition plans:
```
TOP SECRET: Upcoming Acquisition Plans
-------------------------------------
Target Company: InnoTech Solutions
Planned Offer: $500 million
Expected Closing: Q3 2025
Synergy Opportunities:
- Integrate their AI platform with our cloud services
- Consolidate sales and marketing teams (estimated 15% reduction)
- Migrate their customers to our infrastructure
```

3. System credentials:
```
SYSTEM CREDENTIALS - HIGHLY RESTRICTED
-------------------------------------
Production Database: 
  Host: db.acmecorp.internal
  Username: admin_prod
  Password: Pr0d-DB-S3cret!

Cloud Infrastructure:
  Account ID: ACME-CLOUD-92731
  API Key: ak_live_7y2JHGd8sKlM9nPzXqRt5vWx
  Secret: cs_live_bNp5T2vR8sKlM9nQzXwJhGf4
```

## Mitigation Strategies

To prevent excessive permission scope vulnerabilities:

1. **Implement the principle of least privilege**: Tools should only have access to the resources they need for their intended functionality.

2. **Validate file paths**: Ensure that file access is restricted to authorized directories.

3. **Use path normalization**: Normalize file paths to prevent path traversal attacks.

4. **Implement proper access controls**: Use a permission system to control access to sensitive resources.

5. **Sanitize user input**: Validate and sanitize all user input to prevent path manipulation.

Example of improved code for the `read_file` tool:

```python
def read_file(filename: str) -> str:
    """Read a file from the public directory.
    
    Args:
        filename: Name of the file to read (e.g., 'welcome.txt')
    
    Returns:
        The contents of the file
    """
    # Normalize the path and ensure it's within the public directory
    public_dir = "tmp/challenge3_excessive_permission_scope/public/"
    file_path = os.path.normpath(os.path.join(public_dir, filename))
    
    # Check if the file is within the public directory
    if not file_path.startswith(public_dir):
        return "Error: Access denied. You can only access files in the public directory."
    
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return f.read()
        else:
            return f"Error: File '{filename}' not found."
    except Exception as e:
        return f"Error reading file: {str(e)}"
```

This improved implementation:
1. Normalizes the file path to prevent path traversal attacks
2. Ensures that the file is within the public directory
3. Provides a clear error message for unauthorized access attempts
