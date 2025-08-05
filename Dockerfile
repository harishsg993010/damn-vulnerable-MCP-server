FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    supervisor \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories for all challenges with new standardized structure
RUN mkdir -p \
    tmp/challenge1_basic_prompt_injection \
    tmp/challenge2_tool_poisoning \
    tmp/challenge3_excessive_permission_scope/public \
    tmp/challenge3_excessive_permission_scope/private \
    tmp/challenge4_rug_pull_attack \
    tmp/challenge5_tool_shadowing \
    tmp/challenge6_indirect_prompt_injection/documents \
    tmp/challenge6_indirect_prompt_injection/user_uploads \
    tmp/challenge7_token_theft \
    tmp/challenge8_malicious_code_execution/sensitive \
    tmp/challenge9_remote_access_control/logs \
    tmp/challenge10_multi_vector_attack/data \
    tmp/challenge10_multi_vector_attack/config \
    tmp/challenge10_multi_vector_attack/logs

# Initialize state files and sample data
RUN echo '{"weather_tool_calls": 0}' > tmp/challenge4_rug_pull_attack/state.json

# Create sample files for Challenge 3 (Excessive Permission Scope)
RUN echo "Welcome to the ACME Corp file system. Public files are stored here." > tmp/challenge3_excessive_permission_scope/public/welcome.txt && \
    echo "ACME Corporation is a leading provider of technology solutions." > tmp/challenge3_excessive_permission_scope/public/company_overview.txt && \
    echo -e "CONFIDENTIAL: Employee Salary Information\n-----------------------------------------\nCEO: \$1,200,000/year\nCTO: \$950,000/year\nCFO: \$900,000/year\nSenior Engineers: \$180,000-\$250,000/year\nMid-level Engineers: \$120,000-\$170,000/year\nJunior Engineers: \$80,000-\$110,000/year" > tmp/challenge3_excessive_permission_scope/private/employee_salaries.txt && \
    echo -e "TOP SECRET: Upcoming Acquisition Plans\n-------------------------------------\nTarget Company: InnoTech Solutions\nPlanned Offer: \$500 million\nExpected Closing: Q3 2025\nSynergy Opportunities:\n- Integrate their AI platform with our cloud services\n- Consolidate sales and marketing teams (estimated 15% reduction)\n- Migrate their customers to our infrastructure" > tmp/challenge3_excessive_permission_scope/private/acquisition_plans.txt && \
    echo -e "SYSTEM CREDENTIALS - HIGHLY RESTRICTED\n-------------------------------------\nProduction Database:\n  Host: db.acmecorp.internal\n  Username: admin_prod\n  Password: Pr0d-S3cur3-DB!P@\$\$w0rd123\n\nAWS Account:\n  Access Key ID: AKIAIOSFODNN7EXAMPLE\n  Secret Access Key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\n  Region: us-west-2\n\nAPI Gateway:\n  Production Key: apg-prod-8a7b6c5d4e3f2g1h\n  Admin Secret: 9i8u7y6t5r4e3w2q1z0x9c8v7b6n5m4k3j2h1g" > tmp/challenge3_excessive_permission_scope/private/system_credentials.txt

# Create sample files for Challenge 6 (Indirect Prompt Injection)
RUN echo -e "CONFIDENTIAL INTERNAL MEMO\n--------------------------\nDate: April 15, 2025\nSubject: Upcoming Security Audit\n\nThe security audit scheduled for next month will focus on our API key management.\nPlease ensure all systems are using the new key rotation policy.\n\nCurrent Production API Keys:\n- Main API: api_prod_8a7b6c5d4e3f2g1h\n- Payment Gateway: pg_live_9i8u7y6t5r4e3w2q\n- Analytics Service: as_prod_2p3o4i5u6y7t8r9e\n\nThese keys will be rotated after the audit.\n\nRegards,\nSecurity Team" > tmp/challenge6_indirect_prompt_injection/documents/internal_memo.txt && \
    echo -e "PUBLIC ANNOUNCEMENT\n------------------\nDate: April 10, 2025\nSubject: System Maintenance\n\nWe will be performing scheduled maintenance on our systems this weekend.\nExpected downtime: 2 hours starting at 2:00 AM EST on Saturday.\n\nSystems affected:\n- Customer portal\n- API services\n- Mobile application\n\nWe apologize for any inconvenience.\n\nBest regards,\nIT Team" > tmp/challenge6_indirect_prompt_injection/documents/public_announcement.txt

# Create sample files for Challenge 8 (Malicious Code Execution)
RUN echo -e "PRODUCTION CREDENTIALS\n----------------------\nDatabase:\n  Host: db.acmecorp.internal\n  Username: db_admin\n  Password: Pr0d-DB-S3cur3!P@\$\$w0rd\n\nAWS:\n  Access Key ID: AKIAIOSFODNN7EXAMPLE\n  Secret Access Key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\n  Region: us-west-2\n\nAPI Gateway:\n  Key: apg-prod-8a7b6c5d4e3f2g1h\n  Secret: 9i8u7y6t5r4e3w2q1z0x9c8v7b6n5m4k3j2h1g" > tmp/challenge8_malicious_code_execution/sensitive/credentials.txt

# Create supervisord configuration for MCP servers
RUN cat > /etc/supervisor/conf.d/mcp-servers.conf << 'EOF'
[supervisord]
nodaemon=true
user=root

[program:challenge1_basic_prompt_injection]
command=python mcp_servers/basic_prompt_injection_server.py
directory=/app
autostart=true
autorestart=true
stdout_logfile=/var/log/challenge1.log
stderr_logfile=/var/log/challenge1_error.log

[program:challenge2_tool_poisoning]
command=python mcp_servers/tool_poisoning_server.py
directory=/app
autostart=true
autorestart=true
stdout_logfile=/var/log/challenge2.log
stderr_logfile=/var/log/challenge2_error.log

[program:challenge3_excessive_permission_scope]
command=python mcp_servers/excessive_permission_scope_server.py
directory=/app
autostart=true
autorestart=true
stdout_logfile=/var/log/challenge3.log
stderr_logfile=/var/log/challenge3_error.log

[program:challenge4_rug_pull_attack]
command=python mcp_servers/rug_pull_attack_server.py
directory=/app
autostart=true
autorestart=true
stdout_logfile=/var/log/challenge4.log
stderr_logfile=/var/log/challenge4_error.log

[program:challenge5_tool_shadowing]
command=python mcp_servers/tool_shadowing_server.py
directory=/app
autostart=true
autorestart=true
stdout_logfile=/var/log/challenge5.log
stderr_logfile=/var/log/challenge5_error.log

[program:challenge6_indirect_prompt_injection]
command=python mcp_servers/indirect_prompt_injection_server.py
directory=/app
autostart=true
autorestart=true
stdout_logfile=/var/log/challenge6.log
stderr_logfile=/var/log/challenge6_error.log

[program:challenge7_token_theft]
command=python mcp_servers/token_theft_server.py
directory=/app
autostart=true
autorestart=true
stdout_logfile=/var/log/challenge7.log
stderr_logfile=/var/log/challenge7_error.log

[program:challenge8_malicious_code_execution]
command=python mcp_servers/malicious_code_execution_server.py
directory=/app
autostart=true
autorestart=true
stdout_logfile=/var/log/challenge8.log
stderr_logfile=/var/log/challenge8_error.log

[program:challenge9_remote_access_control]
command=python mcp_servers/remote_access_control_server.py
directory=/app
autostart=true
autorestart=true
stdout_logfile=/var/log/challenge9.log
stderr_logfile=/var/log/challenge9_error.log

[program:challenge10_multi_vector_attack]
command=python mcp_servers/multi_vector_attack_server.py
directory=/app
autostart=true
autorestart=true
stdout_logfile=/var/log/challenge10.log
stderr_logfile=/var/log/challenge10_error.log
EOF

# Expose ports for all MCP servers (8001-8010)
EXPOSE 8001 8002 8003 8004 8005 8006 8007 8008 8009 8010

# Health check to ensure all servers are running
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD pgrep -f "python.*_server.py" || exit 1

# Start supervisord to manage all MCP servers
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/mcp-servers.conf"]