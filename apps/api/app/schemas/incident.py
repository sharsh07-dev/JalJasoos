"""Pydantic schemas for Incident models."""
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models.incident import IncidentStatus, IncidentSeverity


class IncidentOut(BaseModel):
    id: UUID
    incident_ref: str
    node_id: UUID
    status: IncidentStatus
    severity: IncidentSeverity
    detection_time: datetime
    localization_time: Optional[datetime] = None
    isolation_time: Optional[datetime] = None
    resolution_time: Optional[datetime] = None
    flow_at_detection: Optional[float] = None
    pressure_at_detection: Optional[float] = None
    acoustic_at_detection: Optional[float] = None
    ai_confidence: Optional[float] = None  # None means model not calibrated
    estimated_loss_liters: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class IncidentEventOut(BaseModel):
    id: UUID
    incident_id: UUID
    timestamp: datetime
    from_status: Optional[IncidentStatus] = None
    to_status: IncidentStatus
    triggered_by: str
    message: str

    class Config:
        from_attributes = True


class IncidentAcknowledge(BaseModel):
    notes: Optional[str] = None


class IncidentUpdateStatus(BaseModel):
    status: IncidentStatus
    notes: Optional[str] = None
    triggered_by: str = "USER"

class IncidentAssign(BaseModel):
    technician_id: UUID

class IncidentFalseAlarm(BaseModel):
    reason: str
