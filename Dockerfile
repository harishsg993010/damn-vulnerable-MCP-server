FROM python:3.11-slim

WORKDIR /app

# Install system dependencies. Challenge 9 shells out to ping, traceroute, and DNS tools.
# Node builds the dashboard that FastAPI serves on port 8081.
RUN apt-get update && apt-get install -y --no-install-recommends \
    supervisor \
    curl \
    iputils-ping \
    traceroute \
    dnsutils \
    net-tools \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Build the dashboard. FastAPI serves dashboard/frontend/dist when that directory exists.
WORKDIR /app/dashboard/frontend
RUN npm install && npm run build
WORKDIR /app

# Copy supervisord configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# startup.sh writes the challenge fixtures, then starts the processes for this role.
RUN chmod +x /app/startup.sh

EXPOSE 8081 9001 9002 9003 9004 9005 9006 9007 9008 9009 9010 9011 9012 9013 9014 9015

# Gateway and single-container roles serve the dashboard. A player container
# only listens on the challenge ports, so either response means the process is up.
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -fs http://localhost:8081/health >/dev/null 2>&1 \
        || curl -s -o /dev/null --max-time 5 http://localhost:9001/mcp \
        || exit 1

CMD ["./startup.sh"]
