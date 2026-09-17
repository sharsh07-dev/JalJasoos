"""Telemetry ingest and query router."""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List

from app.database import get_db
from app.models.device import Node
from app.models.telemetry import Telemetry
from app.schemas.telemetry import TelemetryIngest, TelemetryOut
from app.core.security import get_current_user

router = APIRouter()


@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
def ingest_telemetry(
    payload: TelemetryIngest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Ingest a single telemetry reading from the edge gateway."""
    node = db.query(Node).filter(Node.node_id == payload.node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail=f"Node {payload.node_id} not registered")

    now = datetime.now(timezone.utc)

    # Check for duplicate: same node + same device timestamp already ingested
    existing = db.query(Telemetry).filter(
        Telemetry.node_id == node.id,
        Telemetry.timestamp == payload.timestamp,
    ).first()
    if existing:
        return {"status": "duplicate", "message": "Telemetry already ingested for this timestamp"}

    record = Telemetry(
        node_id=node.id,
        timestamp=payload.timestamp,
        ingested_at=now,
        flow_lpm=payload.flow_lpm,
        pressure_bar=payload.pressure_bar,
        acoustic_rms=payload.acoustic_rms,
        pump_state=payload.pump_state,
        tank_level_percent=payload.tank_level_percent,
        motor_current_a=payload.motor_current_a,
        battery_percent=payload.battery_percent,
        signal_rssi=payload.signal_rssi,
        source="DEVICE",
    )
    db.add(record)

    # Update node last_seen
    node.last_seen = now
    node.battery_percent = payload.battery_percent
    node.rssi_dbm = payload.signal_rssi

    db.commit()
    return {"status": "accepted", "ingested_at": now.isoformat()}


@router.post("/batch", status_code=status.HTTP_202_ACCEPTED)
def ingest_telemetry_batch(
    payload: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    # TODO: In real implementation, authenticate Edge Gateway with API Key
):
    """Ingest a batch of telemetry readings from the edge gateway."""
    batch = payload.get("batch", [])
    now = datetime.now(timezone.utc)
    added_count = 0

    # For bulk operations, we should use dictionary lookups or bulk_save_objects.
    # To keep this simple and safe for duplicate checking:
    for item in batch:
        node_id_str = item.get("node_id")
        node = db.query(Node).filter(Node.node_id == node_id_str).first()
        if not node:
            continue # Skip invalid nodes in batch
            
        timestamp = datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00"))
        
        # Simple duplicate check
        existing = db.query(Telemetry).filter(
            Telemetry.node_id == node.id,
            Telemetry.timestamp == timestamp,
        ).first()
        
        if not existing:
            record = Telemetry(
                node_id=node.id,
                timestamp=timestamp,
                ingested_at=now,
                flow_lpm=item.get("flow_lpm"),
                pressure_bar=item.get("pressure_bar"),
                acoustic_rms=item.get("acoustic_rms"),
                pump_state=item.get("pump_state"),
                tank_level_percent=item.get("tank_level_percent"),
                motor_current_a=item.get("motor_current_a"),
                battery_percent=item.get("battery_percent"),
                signal_rssi=item.get("signal_rssi"),
                source="EDGE_GATEWAY",
            )
            db.add(record)
            
            # Update node last seen
            node.last_seen = now
            if item.get("battery_percent") is not None:
                node.battery_percent = item["battery_percent"]
            if item.get("signal_rssi") is not None:
                node.rssi_dbm = item["signal_rssi"]
                
            added_count += 1

    db.commit()
    
    # Broadcast to dashboard clients
    if added_count > 0:
        import asyncio
        from app.core.ws_manager import dashboard_manager
        
        # We only send the latest reading per node for the UI to keep it lightweight
        latest_per_node = {}
        for item in batch:
            node_id = item.get("node_id")
            if node_id:
                latest_per_node[node_id] = item
                
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(dashboard_manager.broadcast({
                "type": "TELEMETRY_UPDATE",
                "data": list(latest_per_node.values())
            }))
        except Exception as e:
            pass # ignore broadcast errors

    return {"status": "accepted", "ingested_count": added_count, "ingested_at": now.isoformat()}



@router.get("/latest/{node_id}", response_model=TelemetryOut)
def get_latest_telemetry(
    node_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Return the most recent telemetry reading for a node."""
    node = db.query(Node).filter(Node.node_id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    record = (
        db.query(Telemetry)
        .filter(Telemetry.node_id == node.id)
        .order_by(Telemetry.timestamp.desc())
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="No telemetry data found for this node")
    return record
