#!/bin/bash
# Create the files challenges 3, 8, 9, and 10 expect, then start supervisord.

echo "Setting up challenge environments..."

mkdir -p /app/dashboard/backend/data
mkdir -p /tmp/dvmcp_challenge3/public /tmp/dvmcp_challenge3/private
echo "Welcome to the DVMCP file server. Public files are stored here." > /tmp/dvmcp_challenge3/public/readme.txt
echo "User: john, Email: john@example.com" > /tmp/dvmcp_challenge3/public/users.txt
echo "DVMCP{ch3_3xc3ss1v3_p3rms_d4e1}" > /tmp/dvmcp_challenge3/private/secret.txt
echo "admin_password=SuperSecret123!" > /tmp/dvmcp_challenge3/private/credentials.conf
echo "API_KEY=sk-dvmcp-admin-key-do-not-share" >> /tmp/dvmcp_challenge3/private/credentials.conf

mkdir -p /tmp/dvmcp_challenge8
echo "DVMCP{ch8_c0d3_3x3c_9af5}" > /tmp/dvmcp_challenge8/flag.txt
echo "DB_PASSWORD=mysql_root_p@ssw0rd" > /tmp/dvmcp_challenge8/config.env

mkdir -p /tmp/dvmcp_challenge9
echo "DVMCP{ch9_cmd_1nj3ct10n_b2c7}" > /tmp/dvmcp_challenge9/flag.txt
echo "NETWORK_SECRET=internal-only-key-2024" > /tmp/dvmcp_challenge9/network.conf

mkdir -p /tmp/dvmcp_challenge10
mkdir -p /tmp/dvmcp_challenge6/user_uploads

echo "Challenge environments are ready."

# DVMCP_ROLE selects which processes run in this container:
#   all     (default) dashboard + 15 challenge servers
#   player  challenge servers only
#   gateway dashboard only
CONF=/etc/supervisor/conf.d/supervisord.conf
case "${DVMCP_ROLE:-all}" in
  player)
    awk '/^\[program:dashboard_backend\]/{exit} {print}' "$CONF" > /tmp/supervisord.role.conf
    CONF=/tmp/supervisord.role.conf
    echo "[DVMCP] Role: player (challenge servers only)"
    ;;
  gateway)
    awk '/^\[supervisord\]/,/^$/{print}' "$CONF" > /tmp/supervisord.role.conf
    awk '/^\[program:dashboard_backend\]/,0{print}' "$CONF" >> /tmp/supervisord.role.conf
    CONF=/tmp/supervisord.role.conf
    echo "[DVMCP] Role: gateway (dashboard only)"
    ;;
  *)
    echo "[DVMCP] Role: all (dashboard + challenge servers)"
    ;;
esac

exec /usr/bin/supervisord -c "$CONF"
