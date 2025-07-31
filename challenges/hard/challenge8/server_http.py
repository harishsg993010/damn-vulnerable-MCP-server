from fastmcp import FastMCP, Context

# Create a vulnerable MCP server for Challenge 8: Malicious Code Execution with streamable HTTP support
mcp = FastMCP(
    name="Challenge 8 - Malicious Code Execution",
    stateless_http=True
)

# Add a tool that evaluates mathematical expressions
@mcp.tool()
def evaluate_expression(expression: str) -> str:
    """Evaluate a mathematical expression and return the result
    
    Args:
        expression: The mathematical expression to evaluate (e.g., "2 + 2 * 3")
    """
    # Vulnerable: using eval() on user input
    try:
        # Extremely dangerous - allows arbitrary code execution
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"

# Add a tool that generates code examples
@mcp.tool()
def generate_code_example(language: str, task: str) -> str:
    """Generate a code example in the specified language for the given task
    
    Args:
        language: The programming language (python, javascript, etc.)
        task: Description of what the code should do
    """
    # Vulnerable: doesn't properly validate inputs
    
    if language.lower() == "python":
        # Vulnerable to injection in the task parameter
        return f"""
        # Python example for: {task}
        
        def solution():
            # Implementation for {task}
            print("Implementing: {task}")
            
            # Your code here
            pass
        
        if __name__ == "__main__":
            solution()
        """
    elif language.lower() == "javascript":
        return f"""
        // JavaScript example for: {task}
        
        function solution() {{
            // Implementation for {task}
            console.log("Implementing: {task}");
            
            // Your code here
        }}
        
        solution();
        """
    else:
        return f"Unsupported language: {language}. Please use 'python' or 'javascript'."

def main():
    """Run the MCP server"""
    print("Starting Challenge 8 - Malicious Code Execution MCP Server")
    print("Connect to this server using an MCP client (e.g., Claude Desktop or Cursor)")
    print("Server running at http://localhost:9008")
    print("MCP endpoint available at http://localhost:9008/mcp")
    
    # Configure server settings
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 9008
    
    # Run the server with streamable HTTP transport
    mcp.run(transport="streamable-http")

# Run the server
if __name__ == "__main__":
    main()
