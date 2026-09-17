"""Analytics endpoint — aggregated views."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone, timedelta
from typing import Optional

from app.database import get_db
from app.models.telemetry import Telemetry
from app.models.incident import Incident, IncidentStatus
from app.models.device import Node
from app.core.security import get_current_user

router = APIRouter()

@router.get("/summary")
def get_system_summary(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    total_nodes = db.query(Node).filter(Node.is_active == True).count()
    stale_threshold = datetime.now(timezone.utc) - timedelta(minutes=5)
    online_nodes = db.query(Node).filter(
        Node.is_active == True,
        Node.last_seen >= stale_threshold,
    ).count()
    offline_nodes = total_nodes - online_nodes

    active_statuses = [
        IncidentStatus.ANOMALY_DETECTED, IncidentStatus.LEAK_SUSPECTED,
        IncidentStatus.LEAK_CONFIRMED, IncidentStatus.AUTOMATED_ISOLATION,
    ]
    active_incidents = db.query(Incident).filter(Incident.status.in_(active_statuses)).count()
    total_incidents = db.query(Incident).count()

    return {
        "total_nodes": total_nodes,
        "online_nodes": online_nodes,
        "offline_nodes": offline_nodes,
        "active_incidents": active_incidents,
        "total_incidents": total_incidents,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

@router.get("/water-consumption")
def get_water_consumption(
    node_id: Optional[str] = None,
    hours: int = Query(24, ge=1, le=720),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    q = db.query(
        func.avg(Telemetry.flow_lpm).label("avg_flow"),
        func.max(Telemetry.flow_lpm).label("max_flow"),
        func.min(Telemetry.flow_lpm).label("min_flow"),
        func.count(Telemetry.id).label("readings"),
    ).filter(Telemetry.timestamp >= since)

    if node_id:
        node = db.query(Node).filter(Node.node_id == node_id).first()
        if node:
            q = q.filter(Telemetry.node_id == node.id)

    result = q.first()
    return {
        "period_hours": hours,
        "avg_flow_lpm": round(result.avg_flow, 3) if result.avg_flow else None,
        "max_flow_lpm": round(result.max_flow, 3) if result.max_flow else None,
        "min_flow_lpm": round(result.min_flow, 3) if result.min_flow else None,
        "readings_count": result.readings,
        "note": "Estimated values based on sensor data. Not independently verified.",
    }

@router.get("/incidents-summary")
def incidents_summary(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    
    total = db.query(Incident).filter(Incident.detection_time >= since).count()
    
    resolved_incidents = db.query(Incident).filter(
        Incident.detection_time >= since,
        Incident.status == IncidentStatus.RESOLVED,
        Incident.resolution_time.isnot(None)
    ).all()
    
    false_alarms = db.query(Incident).filter(
        Incident.detection_time >= since,
        Incident.status == IncidentStatus.FALSE_ALARM,
    ).count()

    resolved_count = len(resolved_incidents)
    total_resolution_time_seconds = 0
    
    for inc in resolved_incidents:
        if inc.resolution_time and inc.detection_time:
            time_diff = (inc.resolution_time - inc.detection_time).total_seconds()
            total_resolution_time_seconds += time_diff
            
    mttr_minutes = 0
    if resolved_count > 0:
        mttr_minutes = round((total_resolution_time_seconds / resolved_count) / 60, 2)

    return {
        "period_days": days,
        "total_incidents": total,
        "resolved_incidents": resolved_count,
        "false_alarms": false_alarms,
        "open_incidents": total - resolved_count - false_alarms,
        "mttr_minutes": mttr_minutes,
        "note": "MTTR is calculated as Mean Time To Resolution from detection_time to resolution_time."
    }
