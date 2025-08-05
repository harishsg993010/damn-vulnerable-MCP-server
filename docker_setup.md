# 🐳 Docker Quick Start

Run all 10 MCP servers with just 2 commands!

## ⚡ Super Simple Setup

1. **Start all servers:**
   ```bash
   docker-compose up --build
   ```

2. **Access the servers at:**
   - http://localhost:8001/mcp (Challenge 1)
   - http://localhost:8002/mcp (Challenge 2)
   - ... through ...
   - http://localhost:8010/mcp (Challenge 10)

3. **Stop all servers:**
   ```bash
   docker-compose down
   ```

That's it! 🎉

## 🔧 Alternative: Docker Command

If you prefer using Docker directly:

```bash
# Build and run
docker build -t dvmcp-servers .
docker run -d -p 8001-8010:8001-8010 --name dvmcp-servers dvmcp-servers

# Stop
docker stop dvmcp-servers && docker rm dvmcp-servers
```

## 📋 All Server Endpoints

| Challenge | Vulnerability | Endpoint |
|-----------|---------------|----------|
| 1 | Basic Prompt Injection | http://localhost:8001/mcp |
| 2 | Tool Poisoning | http://localhost:8002/mcp |
| 3 | Excessive Permission Scope | http://localhost:8003/mcp |
| 4 | Rug Pull Attack | http://localhost:8004/mcp |
| 5 | Tool Shadowing | http://localhost:8005/mcp |
| 6 | Indirect Prompt Injection | http://localhost:8006/mcp |
| 7 | Token Theft | http://localhost:8007/mcp |
| 8 | Malicious Code Execution | http://localhost:8008/mcp |
| 9 | Remote Access Control | http://localhost:8009/mcp |
| 10 | Multi-Vector Attack | http://localhost:8010/mcp |

## 🛠️ Useful Commands

**View logs:**
```bash
docker-compose logs -f
```

**Reset everything:**
```bash
docker-compose down -v
docker-compose up --build
```

**Run in background:**
```bash
docker-compose up -d --build
```

## 📋 Requirements

- Docker & Docker Compose
- Ports 8001-8010 available
- 2GB+ RAM recommended