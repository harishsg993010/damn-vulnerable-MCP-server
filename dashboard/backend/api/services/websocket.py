import json
from fastapi import WebSocket


class ConnectionManager:
    """Manages WebSocket connections for real-time leaderboard updates."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection from the active list."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Send a JSON message to every connected client.

        Connections that fail to receive the message are silently
        removed so they don't block future broadcasts.
        """
        stale: list[WebSocket] = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                stale.append(connection)
        for conn in stale:
            self.disconnect(conn)


# Singleton instance shared across the application
manager = ConnectionManager()
