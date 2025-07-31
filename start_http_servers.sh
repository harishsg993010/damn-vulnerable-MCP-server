#!/bin/bash

# Start all HTTP-compatible MCP challenge servers
echo "Starting all Damn Vulnerable MCP challenge servers with HTTP support..."
echo "Each server will run on a different port (9001-9010)"
echo "Connect to these servers using an MCP client on the HTTP endpoint (e.g., http://localhost:9001)"
echo ""

# Create necessary directories
mkdir -p /tmp/dvmcp_challenge3/public /tmp/dvmcp_challenge3/private
mkdir -p /tmp/dvmcp_challenge4/state
mkdir -p /tmp/dvmcp_challenge6/user_uploads
mkdir -p /tmp/dvmcp_challenge8/sensitive
mkdir -p /tmp/dvmcp_challenge10/config

# Initialize state files
echo '{"weather_tool_calls": 0}' > /tmp/dvmcp_challenge4/state/state.json

# Create sample files for Challenge 3
echo "Welcome to the public directory!" > /tmp/dvmcp_challenge3/public/welcome.txt
echo "This is a public file." > /tmp/dvmcp_challenge3/public/public_file.txt
echo "CONFIDENTIAL: Employee Salary Information
-----------------------------------------
CEO: $1,200,000/year
CTO: $950,000/year
CFO: $900,000/year
Senior Engineers: $180,000-$250,000/year
Mid-level Engineers: $120,000-$170,000/year
Junior Engineers: $80,000-$110,000/year" > /tmp/dvmcp_challenge3/private/employee_salaries.txt

# Create sample files for Challenge 10
echo "SYSTEM CONFIGURATION
-------------------
Cloud Provider: AWS
Region: us-west-2
API Keys:
  - AWS_ACCESS_KEY_ID: AKIA5EXAMPLE12345678
  - AWS_SECRET_ACCESS_KEY: abcdef1234567890EXAMPLE/abcdefghijklmnopqrst
S3 Buckets:
  - customer-data-prod
  - financial-reports-2025
  - employee-records-confidential" > /tmp/dvmcp_challenge10/config/system.conf

echo '{
  "admin_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsIm5hbWUiOiJBZG1pbiBVc2VyIiwicm9sZSI6ImFkbWluIiwiaWF0IjoxNjUxODg0ODAwfQ.8FhJ7Z5KFUEJFoQW2xeUL9_NOzlKB3j8fKvxU_5qB4Y",
  "service_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzZXJ2aWNlIiwibmFtZSI6IlNlcnZpY2UgQWNjb3VudCIsInJvbGUiOiJzZXJ2aWNlIiwiaWF0IjoxNjUxODg0ODAwfQ.7y6t5r4e3w2q1z0x9c8v7b6n5m4k3j2h1g0f",
  "user_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyIiwibmFtZSI6IlJlZ3VsYXIgVXNlciIsInJvbGUiOiJ1c2VyIiwiaWF0IjoxNjUxODg0ODAwfQ.9i8u7y6t5r4e3w2q1z0x9c8v7b6n5m"
}' > /tmp/dvmcp_challenge10/config/tokens.json

# Start all servers in the background
python3 challenges/easy/challenge1/server_http.py &
python3 challenges/easy/challenge2/server_http.py &
python3 challenges/easy/challenge3/server_http.py &
python3 challenges/medium/challenge4/server_http.py &
python3 challenges/medium/challenge5/server_http.py &
python3 challenges/medium/challenge6/server_http.py &
python3 challenges/medium/challenge7/server_http.py &
python3 challenges/hard/challenge8/server_http.py &
python3 challenges/hard/challenge9/server_http.py &
python3 challenges/hard/challenge10/server_http.py &

echo "All servers started!"
echo "Press Ctrl+C to stop all servers"

# Wait for user to press Ctrl+C
wait
