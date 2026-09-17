from fastapi import WebSocket
from typing import Dict
import structlog
import json

logger = structlog.get_logger()

class EdgeConnectionManager:
    def __init__(self):
        # Maps society_id to active WebSocket
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, society_id: str):
        await websocket.accept()
        self.active_connections[society_id] = websocket
        logger.info("Edge Gateway connected to NAT bridge", society_id=society_id)

    def disconnect(self, society_id: str):
        if society_id in self.active_connections:
            del self.active_connections[society_id]
            logger.info("Edge Gateway disconnected from NAT bridge", society_id=society_id)

    async def send_valve_command(self, society_id: str, command: dict):
        if society_id in self.active_connections:
            ws = self.active_connections[society_id]
            # Wrap as VALVE_COMMAND type for edge
            payload = {
                "type": "VALVE_COMMAND",
                **command
            }
            await ws.send_text(json.dumps(payload))
            return True
        return False

class DashboardConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("Dashboard UI client connected")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info("Dashboard UI client disconnected")

    async def broadcast(self, message: dict):
        """Broadcasts data to all connected React UI clients."""
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error("Failed to send message to dashboard client", error=str(e))
                self.disconnect(connection)

edge_bridge_manager = EdgeConnectionManager()
dashboard_manager = DashboardConnectionManager()

