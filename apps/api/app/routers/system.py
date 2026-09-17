"""System health and administration router."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timezone, timedelta

from app.database import get_db
from app.models.device import Node
from app.core.security import get_current_user, require_roles
from app.models.user import UserRole

router = APIRouter()


@router.get("/health")
def system_health(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception as e:
        pass
        
    stale_threshold = datetime.now(timezone.utc) - timedelta(minutes=5)
    online_nodes = db.query(Node).filter(
        Node.is_active == True,
        Node.last_seen >= stale_threshold,
    ).count()
    total_nodes = db.query(Node).filter(Node.is_active == True).count()

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "api": {"status": "HEALTHY"},
            "database": {"status": "HEALTHY" if db_ok else "OFFLINE"},
        },
        "nodes": {
            "total": total_nodes,
            "online": online_nodes,
            "offline": total_nodes - online_nodes,
        },
    }

@router.post("/simulator/leak")
async def inject_leak(node_id: str):
    """Dynamically trigger a leak in the physical simulator"""
    import paho.mqtt.publish as publish
    import json
    payload = json.dumps({"node_id": node_id, "scenario": "leak"})
    try:
        # Using public hivemq for 100% Docker-free mac environment
        publish.single("jaljasoos/command/simulator/set_scenario", payload, hostname="broker.hivemq.com", port=1883)
    except Exception as e:
        pass
    return {"status": "Leak injected"}

@router.get("/audit-log")
def get_audit_log(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN)),
):
    from app.models.audit import AuditLog
    return (
        db.query(AuditLog)
        .order_by(AuditLog.timestamp.desc())
        .limit(limit)
        .all()
    )


from fastapi import WebSocket, WebSocketDisconnect
from app.core.ws_manager import edge_bridge_manager, dashboard_manager

@router.websocket("/dashboard-ws")
async def dashboard_websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for the Next.js React Dashboard.
    Pushes real-time telemetry, alerts, and valve status updates to the UI.
    """
    await dashboard_manager.connect(websocket)
    try:
        while True:
            # The dashboard only listens, but we can accept keepalives if needed
            data = await websocket.receive_text()
            logger.debug("Received from dashboard", data=data)
    except WebSocketDisconnect:
        dashboard_manager.disconnect(websocket)

@router.websocket("/edge-bridge")
async def edge_websocket_endpoint(websocket: WebSocket):
    """
    Persistent WebSocket for the Edge Gateway.
    This bypasses edge NAT and allows the cloud to push valve commands down.
    """
    # Simple auth mock for prototype - in prod use EDGE_API_KEY checking
    # auth_header = websocket.headers.get("Authorization")
    # For now, we assume society01
    society_id = "society01"
    
    await edge_bridge_manager.connect(websocket, society_id)
    try:
        while True:
            # Keep alive / receive edge acks if needed
            data = await websocket.receive_text()
            logger.info("Received from edge", society_id=society_id, data=data)
    except WebSocketDisconnect:
        edge_bridge_manager.disconnect(society_id)

