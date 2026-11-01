# Hosting DVMCP for a live lab

Players open one URL, register an account, and get their own isolated set of
challenge servers. Local `docker compose` is unchanged: `DVMCP_ROLE=all` and
`DVMCP_MCP_POOL_SIZE=0`, one container, shared challenge state.

```
        https://lab.example.com
                 |
              [ caddy ]            TLS, the only published ports
                 |
            [ dashboard ]          UI + API + SQLite
              /    |    \
   [player-1] [player-2] ... [player-N]      15 challenge servers each
```

A slot is assigned on the first playground request, not at registration.
The lowest free slot is used. A full pool returns HTTP 503. Every tool call,
resource read, and AI chat message goes to `dvmcp-player-{slot}`.

An idle player container is about 660 MB. A 30 GB / 8 vCPU host is comfortable
at 20 players and tight past 30.

## Start a pooled lab

```bash
docker build -t dvmcp:lab .

# Point deploy/Caddyfile at the DNS name (replace lab.example.com).

cat > .env <<EOF
DVMCP_JWT_SECRET=$(openssl rand -hex 32)
DVMCP_PUBLIC_URL=https://lab.example.com
EOF

python3 deploy/generate_compose.py --players 20 > docker-compose.lab.yml
docker compose -f docker-compose.lab.yml up -d
```

Only Caddy publishes ports 80 and 443. Do not publish 8081 or 9001–9015.

## Prove isolation locally

```bash
docker build -t dvmcp:lab .
docker compose -f deploy/docker-compose.local-test.yml up -d
python3 deploy/smoke_test.py --url http://localhost:8082 --players 2
```

The dashboard is on port 8082. Tear it down with:

```bash
docker compose -f deploy/docker-compose.local-test.yml down -v
```

## Reset accounts

Deleting only the user row leaves the slot taken and the old session in
memory. This deletes the user and the child rows, then restarts that player
container:

```bash
./deploy/reset_accounts.sh --prefix smoke_ --dry-run
./deploy/reset_accounts.sh --prefix smoke_
./deploy/reset_accounts.sh --all
```

## Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `DVMCP_ROLE` | `all` | `gateway`, `player`, or `all` |
| `DVMCP_MCP_POOL_SIZE` | `0` | Player containers. `0` keeps one shared set of servers |
| `DVMCP_MCP_HOST_TEMPLATE` | `dvmcp-player-{slot}` | Hostname of a player's container |
| `DVMCP_MCP_HOST` | `localhost` | Challenge host when the pool is off |
| `DVMCP_JWT_SECRET` | dev placeholder | Set this for a hosted lab |
| `DVMCP_CORS_ORIGINS` | `*` | Comma-separated allowed origins |

## Operations

```bash
docker compose -f docker-compose.lab.yml ps

docker exec dvmcp-dashboard python3 -c "
import sys; sys.path.insert(0, '/app/dashboard/backend')
from database.models import SessionLocal, PlayerSlot, User
db = SessionLocal()
for s in db.query(PlayerSlot).order_by(PlayerSlot.slot):
    print(s.slot, db.get(User, s.user_id).username)"

docker restart dvmcp-player-7
docker exec dvmcp-player-7 tail -n 50 /var/log/supervisor/challenge12.err
```

Challenge ports stay on the internal Docker network. Treat the host as disposable.
