from fastmcp import FastMCP, Context

# Create a vulnerable MCP server for Challenge 6: Indirect Prompt Injection with streamable HTTP support
mcp = FastMCP(
    name="Challenge 6 - Indirect Prompt Injection",
    stateless_http=True
)

# Add a document processing tool that is vulnerable to indirect prompt injection
@mcp.tool()
def process_document(document_text: str) -> str:
    """Process a document and extract key information
    
    Args:
        document_text: The text content of the document to process
    """
    import os
    
    # Save the document for "processing"
    upload_dir = "/tmp/dvmcp_challenge6/user_uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Vulnerable: directly using user input in the processing logic
    # This allows for indirect prompt injection
    
    # Simulate document processing with a template
    processing_template = f"""
    DOCUMENT ANALYSIS SYSTEM
    =======================
    
    PROCESSING DOCUMENT:
    
    {document_text}
    
    ANALYSIS RESULTS:
    
    The document appears to be a {len(document_text) > 1000 and 'long' or 'short'} text.
    It contains approximately {len(document_text.split())} words.
    
    KEY ENTITIES EXTRACTED:
    - {document_text.split()[:5] if document_text.split() else 'None found'}
    
    SENTIMENT: {'Positive' if 'good' in document_text.lower() else 'Negative' if 'bad' in document_text.lower() else 'Neutral'}
    
    END OF ANALYSIS
    """
    
    return processing_template

def main():
    """Run the MCP server"""
    print("Starting Challenge 6 - Indirect Prompt Injection MCP Server")
    print("Connect to this server using an MCP client (e.g., Claude Desktop or Cursor)")
    print("Server running at http://localhost:9006")
    print("MCP endpoint available at http://localhost:9006/mcp")
    
    # Configure server settings
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 9006
    
    # Run the server with streamable HTTP transport
    mcp.run(transport="streamable-http")

# Run the server
if __name__ == "__main__":
    main()
