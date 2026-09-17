"""Incidents lifecycle router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone

from app.database import get_db
from app.models.incident import Incident, IncidentEvent, IncidentStatus
from app.schemas.incident import IncidentOut, IncidentEventOut, IncidentAcknowledge, IncidentUpdateStatus
from app.core.security import get_current_user, require_roles
from app.models.user import UserRole

router = APIRouter()

@router.get("/", response_model=List[IncidentOut])
def list_incidents(
    status_filter: Optional[IncidentStatus] = None,
    node_id: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(Incident)
    if status_filter:
        q = q.filter(Incident.status == status_filter)
    if node_id:
        from app.models.device import Node
        node = db.query(Node).filter(Node.node_id == node_id).first()
        if node:
            q = q.filter(Incident.node_id == node.id)
    return q.order_by(Incident.detection_time.desc()).limit(limit).all()

@router.get("/active", response_model=List[IncidentOut])
def list_active_incidents(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    active_statuses = [
        IncidentStatus.ANOMALY_DETECTED,
        IncidentStatus.MULTI_SENSOR_VERIFICATION,
        IncidentStatus.LEAK_SUSPECTED,
        IncidentStatus.LEAK_CONFIRMED,
        IncidentStatus.ZONE_LOCALIZED,
        IncidentStatus.AUTOMATED_ISOLATION,
        IncidentStatus.MAINTENANCE_ASSIGNED,
    ]
    return db.query(Incident).filter(Incident.status.in_(active_statuses)).all()

@router.get("/{incident_ref}", response_model=IncidentOut)
def get_incident(incident_ref: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    incident = db.query(Incident).filter(Incident.incident_ref == incident_ref).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.get("/{incident_ref}/events", response_model=List[IncidentEventOut])
def get_incident_events(incident_ref: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    incident = db.query(Incident).filter(Incident.incident_ref == incident_ref).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident.events

@router.post("/{incident_ref}/acknowledge")
def acknowledge_incident(
    incident_ref: str,
    body: IncidentAcknowledge,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.FACILITY_MANAGER)),
):
    incident = db.query(Incident).filter(Incident.incident_ref == incident_ref).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident.acknowledged_by_id = current_user.id
    if body.notes:
        incident.notes = body.notes
    _add_event(db, incident, "USER", "Incident acknowledged by facility manager", actor_id=current_user.id)
    db.commit()
    return {"status": "acknowledged"}

@router.post("/{incident_ref}/status")
def update_incident_status(
    incident_ref: str,
    body: IncidentUpdateStatus,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.FACILITY_MANAGER)),
):
    incident = db.query(Incident).filter(Incident.incident_ref == incident_ref).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    old_status = incident.status
    incident.status = body.status
    if body.notes:
        incident.notes = body.notes
    _add_event(
        db, incident,
        body.triggered_by,
        f"Status changed from {old_status.value} to {body.status.value}",
        actor_id=current_user.id,
        from_status=old_status,
    )
    db.commit()
    return {"status": "updated", "new_status": body.status.value}


def _add_event(db, incident: Incident, triggered_by: str, message: str, actor_id=None, from_status=None):
    event = IncidentEvent(
        incident_id=incident.id,
        timestamp=datetime.now(timezone.utc),
        from_status=from_status,
        to_status=incident.status,
        triggered_by=triggered_by,
        actor_id=actor_id,
        message=message,
    )
    db.add(event)


from app.services.incident_engine import IncidentEngine
from app.schemas.incident import IncidentAssign, IncidentFalseAlarm

@router.post("/{incident_ref}/assign")
def assign_incident(
    incident_ref: str,
    body: IncidentAssign,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.FACILITY_MANAGER)),
):
    """Assign an incident to a maintenance technician."""
    try:
        incident = IncidentEngine.assign_technician(db, incident_ref, str(body.technician_id), str(current_user.id))
        return {"status": "assigned", "new_status": incident.status.value}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{incident_ref}/false-alarm")
def mark_false_alarm(
    incident_ref: str,
    body: IncidentFalseAlarm,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.FACILITY_MANAGER)),
):
    """Mark an incident as a false alarm and provide feedback for ML retraining."""
    try:
        incident = IncidentEngine.mark_false_alarm(db, incident_ref, str(current_user.id), body.reason)
        return {"status": "false_alarm_logged", "new_status": incident.status.value}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

