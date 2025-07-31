# Cursor SSE Compatibility for Damn Vulnerable MCP

This document provides an overview of the updates made to the Damn Vulnerable Model Context Protocol (DVMCP) project to make it compatible with Cursor's Server-Sent Events (SSE) implementation.

## Overview

The original DVMCP project has been enhanced to support Cursor's SSE implementation, allowing the challenge servers to be accessed directly from Cursor. This makes the challenges more accessible and realistic, as they can be tested with a real-world MCP client.

## Implementation Changes

Each challenge server now has an SSE-compatible version (`server_sse.py`) that implements:

1. **SSE Transport Layer**: Using the MCP library's `SseServerTransport` class
2. **FastAPI Integration**: Using FastAPI and Starlette for routing and server implementation
3. **Endpoint Configuration**: Exposing the `/sse` endpoint required by Cursor
4. **Port Assignments**: Using unique ports (9001-9010) to avoid conflicts

## Directory Structure

```
damn-vulnerable-mcs/
├── challenges/
│   ├── easy/
│   │   ├── challenge1/
│   │   │   ├── server.py          # Original server
│   │   │   └── server_sse.py      # SSE-compatible server
│   │   ├── challenge2/
│   │   │   ├── server.py
│   │   │   └── server_sse.py
│   │   └── challenge3/
│   │       ├── server.py
│   │       └── server_sse.py
│   ├── medium/
│   │   ├── challenge4/
│   │   │   ├── server.py
│   │   │   └── server_sse.py
│   │   ├── challenge5/
│   │   │   ├── server.py
│   │   │   └── server_sse.py
│   │   ├── challenge6/
│   │   │   ├── server.py
│   │   │   └── server_sse.py
│   │   └── challenge7/
│   │       ├── server.py
│   │       └── server_sse.py
│   └── hard/
│       ├── challenge8/
│       │   ├── server.py
│       │   └── server_sse.py
│       ├── challenge9/
│       │   ├── server.py
│       │   └── server_sse.py
│       └── challenge10/
│           ├── server.py
│           └── server_sse.py
├── docs/
│   ├── cursor_sse_compatibility.md    # This document
│   └── ... (other documentation)
├── start_sse_servers.sh               # Script to start all SSE servers
└── requirements.txt                   # Updated dependencies
```

## Running the SSE-Compatible Servers

You can run individual servers:

```bash
python3 challenges/easy/challenge1/server_sse.py
```

Or use the provided script to start all servers:

```bash
./start_sse_servers.sh
```

## Connecting with Cursor

To connect to an SSE-compatible server using Cursor:

1. Start the server
2. In Cursor, configure the MCP connection to use the SSE endpoint (e.g., `http://localhost:9001/sse`)
3. Cursor will automatically detect the SSE transport and establish a connection

## Dependencies

The following dependencies have been added to support SSE compatibility:

```
fastapi>=0.95.0
uvicorn>=0.21.1
httpx>=0.24.0
mcp[cli]>=0.5.0
starlette>=0.27.0
```

## Port Assignments

Each challenge server uses a unique port:

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

## Security Considerations

The SSE implementation maintains all the same vulnerabilities as the original implementation, ensuring that the challenges remain educational for security researchers.

For detailed implementation information, see the [Cursor SSE Compatibility Guide](cursor_sse_compatibility.md).
