#!/bin/bash

# Script to stop all running MCP servers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Stopping all MCP servers...${NC}"

# Kill processes by port (if lsof is available)
if command -v lsof >/dev/null 2>&1; then
    echo -e "${YELLOW}Stopping servers by port...${NC}"
    
    for port in {8001..8010}; do
        pid=$(lsof -ti:$port 2>/dev/null || true)
        if [ ! -z "$pid" ]; then
            kill "$pid" 2>/dev/null || true
            echo -e "${GREEN}Stopped server on port $port (PID: $pid)${NC}"
        fi
    done
else
    echo -e "${YELLOW}lsof not available, using pkill...${NC}"
fi

# Also try to kill by process name pattern
echo -e "${YELLOW}Stopping servers by process name...${NC}"
pkill -f "python.*_server.py" 2>/dev/null || true

# Give processes a moment to shut down gracefully
sleep 2

# Force kill any remaining processes
echo -e "${YELLOW}Force killing any remaining server processes...${NC}"
pkill -9 -f "python.*_server.py" 2>/dev/null || true

echo -e "${GREEN}All MCP servers stopped.${NC}"