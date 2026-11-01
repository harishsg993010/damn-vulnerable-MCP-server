#!/usr/bin/env bash
# Delete player accounts and wipe the containers those accounts were using.
#
# The account database lives in the dashboard container. Challenge session
# state lives in the player container for that slot. Deleting the account
# frees the slot, then this script restarts that container so the next
# player starts clean.
#
#   ./deploy/reset_accounts.sh --prefix smoke_ --dry-run
#   ./deploy/reset_accounts.sh --prefix smoke_
#   ./deploy/reset_accounts.sh --all
#
# Defaults match a stack from deploy/generate_compose.py. The two-player
# local test uses different container names:
#   DVMCP_DASHBOARD_CONTAINER=dvmcp-test-dashboard \
#   DVMCP_PLAYER_CONTAINER_TEMPLATE='dvmcp-test-player-%s' \
#   ./deploy/reset_accounts.sh --prefix smoke_

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DASHBOARD_CONTAINER="${DVMCP_DASHBOARD_CONTAINER:-dvmcp-dashboard}"
PLAYER_CONTAINER_TEMPLATE="${DVMCP_PLAYER_CONTAINER_TEMPLATE:-dvmcp-player-%s}"

if ! docker inspect "$DASHBOARD_CONTAINER" >/dev/null 2>&1; then
  echo "$DASHBOARD_CONTAINER is not running" >&2
  exit 1
fi

docker cp "$ROOT/deploy/reset_accounts.py" "$DASHBOARD_CONTAINER":/tmp/reset_accounts.py

output="$(docker exec "$DASHBOARD_CONTAINER" python3 /tmp/reset_accounts.py "$@")"
printf '%s\n' "$output"

dry_run=0
for arg in "$@"; do
  if [[ "$arg" == "--dry-run" ]]; then
    dry_run=1
  fi
done

if [[ "$dry_run" -eq 1 ]]; then
  exit 0
fi

slots="$(printf '%s\n' "$output" | awk '/^FREED_SLOT / {print $2}')"
if [[ -z "$slots" ]]; then
  echo "No player containers to restart."
  exit 0
fi

for slot in $slots; do
  name="$(printf "$PLAYER_CONTAINER_TEMPLATE" "$slot")"
  if docker inspect "$name" >/dev/null 2>&1; then
    echo "Restarting ${name} to clear the previous player's session."
    docker restart "$name" >/dev/null
  else
    echo "No container named ${name}; the slot was freed in the database only." >&2
  fi
done
