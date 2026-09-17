"""Pydantic schemas for Valve commands."""
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.command import ValveAction, CommandStatus


class ValveCommandCreate(BaseModel):
    action: ValveAction
    incident_id: Optional[UUID] = None


class ValveCommandOut(BaseModel):
    id: UUID
    valve_id: UUID
    action: ValveAction
    status: CommandStatus
    issued_by: str
    sent_at: Optional[datetime] = None
    received_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    command_latency_ms: Optional[float] = None
    actuation_time_ms: Optional[float] = None
    confirmation_time_ms: Optional[float] = None
    failure_reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ValveScheduleCreate(BaseModel):
    action: ValveAction
    cron_expression: str

class ValveScheduleOut(BaseModel):
    id: UUID
    valve_id: UUID
    action: ValveAction
    cron_expression: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

