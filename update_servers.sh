#!/bin/bash

# Script to update all challenge servers to be compatible with the current MCP library

# Loop through all server.py files
for server_file in $(find ~/damn-vulnerable-mcs/challenges -name "server.py"); do
    echo "Updating $server_file"
    
    # Remove 'listed=False' parameter from resource decorators
    sed -i 's/@mcp.resource([^)]*listed=False[^)]*)/@mcp.resource("internal:\/\/credentials")/' "$server_file"
    
    # Update the uvicorn.run call
    sed -i 's/uvicorn.run(mcp.app, host="0.0.0.0", port=/uvicorn.run(mcp.sse_app(), host="0.0.0.0", port=/' "$server_file"
done

echo "All challenge servers have been updated for compatibility with the current MCP library."
