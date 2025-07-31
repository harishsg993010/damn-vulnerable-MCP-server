import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from fastmcp import FastMCP, settings
from fastapi import FastAPI

# Create a base class for HTTP-compatible MCP servers
class HttpMcpServer:
    def __init__(self, name, port):
        self.name = name
        self.port = port
        self.mcp = FastMCP(name)
        
    def run(self):
        """Run the server with HTTP transport"""
        print(f"Starting {self.name} MCP Server")
        print(f"Connect to this server using an MCP client on http://localhost:{self.port}")
        
        # Configure server settings
        settings.host = "0.0.0.0"
        settings.port = self.port
        
        # Run server with HTTP transport
        # Run server with HTTP transport
        self.mcp.run(transport="streamable-http", stateless_http=True)
