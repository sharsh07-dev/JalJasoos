"""Nodes router — device registry + status."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone, timedelta

from app.database import get_db
from app.models.device import Node, NodeStatus
from app.schemas.device import NodeCreate, NodeOut
from app.core.security import get_current_user, require_roles
from app.models.user import UserRole

router = APIRouter()

STALE_THRESHOLD_MINUTES = 5  # Node is stale if not seen in 5 min

@router.get("/", response_model=List[NodeOut])
def list_nodes(
    zone_id: Optional[str] = None,
    status: Optional[NodeStatus] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(Node).filter(Node.is_active == True)
    if zone_id:
        q = q.filter(Node.zone_id == zone_id)
    if status:
        q = q.filter(Node.status == status)
    return q.all()

@router.post("/", response_model=NodeOut, status_code=status.HTTP_201_CREATED)
def register_node(
    payload: NodeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.FACILITY_MANAGER)),
):
    existing = db.query(Node).filter(Node.node_id == payload.node_id).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Node {payload.node_id} already registered")
    node = Node(**payload.model_dump())
    db.add(node)
    db.commit()
    db.refresh(node)
    return node

@router.get("/{node_id}", response_model=NodeOut)
def get_node(node_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    node = db.query(Node).filter(Node.node_id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node

@router.get("/{node_id}/telemetry")
def get_node_telemetry(
    node_id: str,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.models.telemetry import Telemetry
    from app.schemas.telemetry import TelemetryOut
    node = db.query(Node).filter(Node.node_id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    records = (
        db.query(Telemetry)
        .filter(Telemetry.node_id == node.id)
        .order_by(Telemetry.timestamp.desc())
        .limit(limit)
        .all()
    )
    return records
