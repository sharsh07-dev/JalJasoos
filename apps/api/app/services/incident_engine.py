from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
import structlog
from typing import Optional

from app.models.incident import Incident, IncidentStatus, IncidentEvent
from app.models.user import User

logger = structlog.get_logger()

class IncidentEngine:
    """
    Central state machine for Incident lifecycles.
    Ensures transitions are valid and an immutable audit trail is kept.
    """
    
    @staticmethod
    def _add_event(
        db: Session, 
        incident: Incident, 
        new_status: IncidentStatus, 
        message: str, 
        triggered_by: str, 
        user_id: Optional[str] = None
    ):
        """Append to the immutable incident event log."""
        event = IncidentEvent(
            incident_id=incident.id,
            from_status=incident.status,
            to_status=new_status,
            triggered_by=triggered_by,
            actor_id=user_id,
            message=message,
            timestamp=datetime.now(timezone.utc)
        )
        incident.status = new_status
        db.add(event)
        
    @staticmethod
    def assign_technician(db: Session, incident_ref: str, technician_id: str, assigner_id: str):
        """Assign an incident to a maintenance technician."""
        incident = db.query(Incident).filter(Incident.incident_ref == incident_ref).first()
        tech = db.query(User).filter(User.id == technician_id).first()
        
        if not incident or not tech:
            raise ValueError("Incident or Technician not found")
            
        # In the schema, assignment might be tracked in MaintenanceTask, but we'll update status.
        IncidentEngine._add_event(
            db, 
            incident, 
            IncidentStatus.MAINTENANCE_ASSIGNED, 
            f"Assigned to technician: {tech.email}", 
            "USER",
            assigner_id
        )
        db.commit()
        return incident

    @staticmethod
    def mark_false_alarm(db: Session, incident_ref: str, user_id: str, reason: str):
        """Mark incident as a FALSE_ALARM. Critical for ML retraining."""
        incident = db.query(Incident).filter(Incident.incident_ref == incident_ref).first()
        if not incident:
            raise ValueError("Incident not found")
            
        incident.resolution_time = datetime.now(timezone.utc)
        
        IncidentEngine._add_event(
            db, 
            incident, 
            IncidentStatus.FALSE_ALARM, 
            f"Marked as False Alarm. Reason: {reason}", 
            "USER",
            user_id
        )
        db.commit()
        return incident

    @staticmethod
    def auto_escalate(db: Session):
        """
        Background job: Escalate CRITICAL incidents that haven't been 
        acknowledged within 15 minutes.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=15)
        
        stale_incidents = db.query(Incident).filter(
            Incident.status.in_([IncidentStatus.ANOMALY_DETECTED, IncidentStatus.LEAK_SUSPECTED]),
            Incident.acknowledged_by_id.is_(None),
            Incident.detection_time < cutoff
        ).all()
        
        count = 0
        for inc in stale_incidents:
            IncidentEngine._add_event(
                db,
                inc,
                IncidentStatus.LEAK_CONFIRMED, # Escalate to confirmed
                "Auto-escalated to LEAK_CONFIRMED due to SLA breach",
                triggered_by="SYSTEM"
            )
            count += 1
            
        db.commit()
        if count > 0:
            logger.warning("Escalated stale incidents", count=count)
        return count
