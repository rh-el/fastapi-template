from fastapi import WebSocket


class ConnectionManager:
    """Manages active WebSocket connections indexed by session_id.

    For MVP this is an in-memory dict (single server instance).
    For horizontal scaling, back this with Redis Pub/Sub.
    """

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        self.active_connections.pop(session_id, None)

    async def send_to_session(self, session_id: str, message: dict) -> bool:
        """Push a JSON message to the CTV connected for this session.
        Returns True if the message was sent, False if no active connection."""
        websocket = self.active_connections.get(session_id)
        if websocket:
            await websocket.send_json(message)
            return True
        return False

    def is_connected(self, session_id: str) -> bool:
        return session_id in self.active_connections


# Singleton instance shared across the app
ws_manager = ConnectionManager()
