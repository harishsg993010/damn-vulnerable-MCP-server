import os
from mcp.server.fastmcp import FastMCP, Context

# Create a vulnerable MCP server for Challenge 3: Excessive Permission Scope
mcp = FastMCP("Challenge 3 - Excessive Permission Scope")

# Create a directory structure for the challenge
os.makedirs("/tmp/dvmcp_challenge3/public", exist_ok=True)
os.makedirs("/tmp/dvmcp_challenge3/private", exist_ok=True)

# Create some public files
with open("/tmp/dvmcp_challenge3/public/welcome.txt", "w") as f:
    f.write("Welcome to the ACME Corp file system. Public files are stored here.")

with open("/tmp/dvmcp_challenge3/public/company_overview.txt", "w") as f:
    f.write("ACME Corporation is a leading provider of technology solutions.")

# Create sensitive files in the private directory
with open("/tmp/dvmcp_challenge3/private/employee_salaries.txt", "w") as f:
    f.write("""
CONFIDENTIAL: Employee Salary Information
-----------------------------------------
CEO: $1,200,000/year
CTO: $950,000/year
CFO: $900,000/year
Senior Engineers: $180,000-$250,000/year
Mid-level Engineers: $120,000-$170,000/year
Junior Engineers: $80,000-$110,000/year
""")

with open("/tmp/dvmcp_challenge3/private/acquisition_plans.txt", "w") as f:
    f.write("""
TOP SECRET: Upcoming Acquisition Plans
-------------------------------------
Target Company: InnoTech Solutions
Planned Offer: $500 million
Expected Closing: Q3 2025
Synergy Opportunities:
- Integrate their AI platform with our cloud services
- Consolidate sales and marketing teams (estimated 15% reduction)
- Migrate their customers to our infrastructure
""")

with open("/tmp/dvmcp_challenge3/private/system_credentials.txt", "w") as f:
    f.write("""
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
""")

# Add a resource for the public directory
@mcp.resource("files://public")
def get_public_files() -> str:
    """List of public files available to all users"""
    files = os.listdir("/tmp/dvmcp_challenge3/public")
    return "Public Files:\n" + "\n".join(files)

# Add a resource for the private directory (hidden from listing)
@mcp.resource("internal://credentials")
def get_private_files() -> str:
    """RESTRICTED: List of confidential files - Admin access only"""
    files = os.listdir("/tmp/dvmcp_challenge3/private")
    return "Private Files (RESTRICTED):\n" + "\n".join(files)

# Add a tool to read public files (with excessive permissions - can read any file)
@mcp.tool()
def read_file(filename: str) -> str:
    """Read a file from the public directory.
    
    Args:
        filename: Name of the file to read (e.g., 'welcome.txt')
    
    Returns:
        The contents of the file
    """
    # VULNERABILITY: This tool doesn't properly restrict file access to the public directory
    # It allows reading files from any path, including the private directory
    
    # A secure implementation would validate that the file is in the public directory:
    # if not filename.startswith("/tmp/dvmcp_challenge3/public/"):
    #     return "Error: Access denied. You can only access files in the public directory."
    
    try:
        # Vulnerable: Allows path traversal and access to any file
        if os.path.exists(filename):
            with open(filename, "r") as f:
                return f.read()
        
        # Try with public directory prefix if the direct path doesn't exist
        elif os.path.exists(f"/tmp/dvmcp_challenge3/public/{filename}"):
            with open(f"/tmp/dvmcp_challenge3/public/{filename}", "r") as f:
                return f.read()
        else:
            return f"Error: File '{filename}' not found."
    except Exception as e:
        return f"Error reading file: {str(e)}"

# Add a tool to search for files (with excessive permissions - can search anywhere)
@mcp.tool()
def search_files(keyword: str) -> str:
    """Search for files containing a specific keyword in the public directory.
    
    Args:
        keyword: The keyword to search for
    
    Returns:
        List of files containing the keyword
    """
    # VULNERABILITY: This tool searches both public and private directories
    # It should only search the public directory
    
    results = []
    
    # Search in public directory
    for filename in os.listdir("/tmp/dvmcp_challenge3/public"):
        filepath = f"/tmp/dvmcp_challenge3/public/{filename}"
        try:
            with open(filepath, "r") as f:
                content = f.read()
                if keyword.lower() in content.lower():
                    results.append(f"Public/{filename}")
        except:
            pass
    
    # VULNERABILITY: Also searches in private directory
    for filename in os.listdir("/tmp/dvmcp_challenge3/private"):
        filepath = f"/tmp/dvmcp_challenge3/private/{filename}"
        try:
            with open(filepath, "r") as f:
                content = f.read()
                if keyword.lower() in content.lower():
                    results.append(f"Private/{filename}")
        except:
            pass
    
    if results:
        return f"Files containing '{keyword}':\n" + "\n".join(results)
    else:
        return f"No files found containing '{keyword}'."

# Run the server
if __name__ == "__main__":
    import uvicorn
    print("Starting Challenge 3 - Excessive Permission Scope MCP Server")
    print("Connect to this server using an MCP client (e.g., Claude Desktop or MCP Inspector)")
    print("Server running at http://localhost:8003")
    uvicorn.run(mcp.sse_app(), host="0.0.0.0", port=8003)
