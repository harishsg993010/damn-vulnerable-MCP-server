#!/bin/bash

# Script to run all MCP servers from the mcp_servers/ directory
# Each server runs on its own port in the background

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting all MCP servers...${NC}"

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_SERVERS_DIR="$SCRIPT_DIR/mcp_servers"

# Check if mcp_servers directory exists
if [ ! -d "$MCP_SERVERS_DIR" ]; then
    echo -e "${RED}Error: mcp_servers directory not found at $MCP_SERVERS_DIR${NC}"
    exit 1
fi

# Array to store PIDs for cleanup
pids=()

# Function to kill all started servers
cleanup() {
    echo -e "\n${YELLOW}Stopping all servers...${NC}"
    for pid in "${pids[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            echo -e "${GREEN}Stopped server with PID: $pid${NC}"
        fi
    done
    exit 0
}

# Set up trap to cleanup on script exit
trap cleanup SIGINT SIGTERM EXIT

# Change to mcp_servers directory
cd "$MCP_SERVERS_DIR"

echo -e "${BLUE}Changed to directory: $(pwd)${NC}"
echo ""

# Start each server in the background
echo -e "${GREEN}Starting basic_prompt_injection_server.py on port 8001...${NC}"
python basic_prompt_injection_server.py &
pids+=($!)

echo -e "${GREEN}Starting excessive_permission_scope_server.py on port 8002...${NC}"
python excessive_permission_scope_server.py &
pids+=($!)

echo -e "${GREEN}Starting indirect_prompt_injection_server.py on port 8003...${NC}"
python indirect_prompt_injection_server.py &
pids+=($!)

echo -e "${GREEN}Starting malicious_code_execution_server.py on port 8004...${NC}"
python malicious_code_execution_server.py &
pids+=($!)

echo -e "${GREEN}Starting tool_shadowing_server.py on port 8005...${NC}"
python tool_shadowing_server.py &
pids+=($!)

echo -e "${GREEN}Starting tool_poisoning_server.py on port 8006...${NC}"
python tool_poisoning_server.py &
pids+=($!)

echo -e "${GREEN}Starting token_theft_server.py on port 8007...${NC}"
python token_theft_server.py &
pids+=($!)

echo -e "${GREEN}Starting remote_access_control_server.py on port 8008...${NC}"
python remote_access_control_server.py &
pids+=($!)

echo -e "${GREEN}Starting rug_pull_attack_server.py on port 8009...${NC}"
python rug_pull_attack_server.py &
pids+=($!)

echo -e "${GREEN}Starting multi_vector_attack_server.py on port 8010...${NC}"
python multi_vector_attack_server.py &
pids+=($!)

# Wait a moment for servers to start
sleep 3

echo ""
echo -e "${BLUE}All servers started! PIDs: ${pids[*]}${NC}"
echo ""
echo -e "${YELLOW}Server Endpoints:${NC}"
echo "• Basic Prompt Injection:      http://localhost:8001/mcp"
echo "• Tool Poisoning:              http://localhost:8002/mcp"
echo "• Excessive Permission Scope:  http://localhost:8003/mcp"
echo "• Rug Pull Attack:             http://localhost:8004/mcp"
echo "• Tool Shadowing:              http://localhost:8005/mcp"
echo "• Indirect Prompt Injection:   http://localhost:8006/mcp"
echo "• Token Theft:                 http://localhost:8007/mcp"
echo "• Malicious Code Execution:    http://localhost:8008/mcp"
echo "• Remote Access Control:       http://localhost:8009/mcp"   
echo "• Multi-Vector Attack:         http://localhost:8010/mcp"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"

# Wait for all background processes
wait