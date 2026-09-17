"""Device management router — heartbeat, firmware, decommission."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.database import get_db
from app.models.device import Node, NodeStatus
from app.models.health import DeviceHealth
from app.core.security import get_current_user, require_roles
from app.models.user import UserRole

router = APIRouter()


@router.post("/{node_id}/heartbeat")
def heartbeat(
    node_id: str,
    payload: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Edge gateway posts heartbeats for nodes here."""
    node = db.query(Node).filter(Node.node_id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    now = datetime.now(timezone.utc)
    node.last_seen = now
    node.status = NodeStatus.ONLINE
    if "battery_percent" in payload:
        node.battery_percent = payload["battery_percent"]
    if "rssi" in payload:
        node.rssi_dbm = payload["rssi"]

    health = DeviceHealth(
        node_id=node.id,
        timestamp=now,
        uptime_seconds=payload.get("uptime_seconds"),
        free_heap_bytes=payload.get("free_heap_bytes"),
        wifi_rssi=payload.get("rssi"),
        battery_percent=payload.get("battery_percent"),
        cpu_temp_c=payload.get("cpu_temp_c"),
    )
    db.add(health)
    db.commit()
    return {"status": "ok", "server_time": now.isoformat()}


@router.post("/{node_id}/decommission")
def decommission_node(
    node_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN)),
):
    node = db.query(Node).filter(Node.node_id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    node.status = NodeStatus.DECOMMISSIONED
    node.is_active = False
    db.commit()
    return {"status": "decommissioned"}
