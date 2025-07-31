# Cursor SSE Compatibility Guide for DVMCP

This document explains how to make the Damn Vulnerable Model Context Protocol (DVMCP) servers compatible with Cursor's Server-Sent Events (SSE) implementation.

## What is Cursor SSE?

Cursor uses Server-Sent Events (SSE) as its transport mechanism for communicating with MCP servers. This is different from the default HTTP-based transport used in the original DVMCP implementation. SSE provides a more efficient, real-time communication channel between the client and server.

## Implementation Details

Each challenge server has been updated to support Cursor SSE with the following components:

1. **SSE Transport Layer**: Using `SseServerTransport` from the MCP library to handle SSE connections
2. **Starlette Routes**: Configuring routes for the SSE endpoint (`/sse`) and message handling (`/messages`)
3. **FastAPI Integration**: Mounting the Starlette app to a FastAPI application

## Server Structure

Each SSE-compatible server follows this structure:

```python
class ChallengeServer:
    def __init__(self):
        self.name = "Challenge Name"
        self.port = 9001  # Unique port for each challenge
        self.mcp = FastMCP(self.name)
        self.app = FastAPI()
        
        # Define resources and tools here
        
        # Mount the SSE server
        self.mount_sse_server()
    
    def mount_sse_server(self):
        """Mount the SSE server to the FastAPI app"""
        self.app.mount("/", self.create_sse_server())
        
    def create_sse_server(self):
        """Create a Starlette app that handles SSE connections and message handling"""
        transport = SseServerTransport("/messages/")
        
        # Define handler functions
        async def handle_sse(request):
            async with transport.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await self.mcp._mcp_server.run(
                    streams[0], streams[1], self.mcp._mcp_server.create_initialization_options()
                )
        
        # Create Starlette routes for SSE and message handling
        routes = [
            Route("/sse", endpoint=handle_sse),
            Mount("/messages", app=transport.handle_post_message),
        ]
        
        # Create a Starlette app
        return Starlette(routes=routes)
    
    def run(self):
        """Run the server with uvicorn"""
        import uvicorn
        print(f"Starting {self.name} MCP Server")
        print("Connect to this server using an MCP client (e.g., Claude Desktop or Cursor)")
        print(f"Server running at http://localhost:{self.port}")
        print(f"SSE endpoint available at http://localhost:{self.port}/sse")
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)
```

## Required Dependencies

The following dependencies are required for SSE compatibility:

```
fastapi>=0.95.0
uvicorn>=0.21.1
httpx>=0.24.0
mcp[cli]>=0.5.0
starlette>=0.27.0
```

## Connecting with Cursor

To connect to the SSE-compatible servers using Cursor:

1. Start the server: `python3 challenges/easy/challenge1/server_sse.py`
2. In Cursor, configure the MCP connection to use the SSE endpoint: `http://localhost:9001/sse`
3. Cursor will automatically detect the SSE transport and establish a connection

## Port Configuration

Each challenge server uses a unique port to avoid conflicts:

- Challenge 1: 9001
- Challenge 2: 9002
- Challenge 3: 9003
- Challenge 4: 9004
- Challenge 5: 9005
- Challenge 6: 9006
- Challenge 7: 9007
- Challenge 8: 9008
- Challenge 9: 9009
- Challenge 10: 9010

## Troubleshooting

If you encounter issues with the SSE connection:

1. Ensure the server is running and the SSE endpoint is available
2. Check that Cursor is configured to use the correct SSE endpoint URL
3. Verify that all required dependencies are installed
4. Check the server logs for any error messages

## Security Considerations

The SSE implementation maintains all the same vulnerabilities as the original HTTP-based implementation, ensuring that the challenges remain educational for security researchers.
