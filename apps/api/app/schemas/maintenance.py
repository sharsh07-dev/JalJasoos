"""Pydantic schemas for Maintenance tasks and logs."""
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models.maintenance import MaintenanceStatus, MaintenancePriority


class MaintenanceTaskCreate(BaseModel):
    incident_id: UUID
    title: str
    description: Optional[str] = None
    priority: MaintenancePriority = MaintenancePriority.MEDIUM
    assigned_to_id: Optional[UUID] = None
    due_date: Optional[datetime] = None


class MaintenanceTaskOut(BaseModel):
    id: UUID
    task_ref: str
    incident_id: UUID
    assigned_to_id: Optional[UUID] = None
    status: MaintenanceStatus
    priority: MaintenancePriority
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MaintenanceLogCreate(BaseModel):
    note: Optional[str] = None
    action_taken: Optional[str] = None
    attachments: Optional[List[str]] = None


class MaintenanceLogOut(BaseModel):
    id: UUID
    task_id: UUID
    logged_by_id: UUID
    note: Optional[str] = None
    action_taken: Optional[str] = None
    attachments: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MaintenanceTaskStatusUpdate(BaseModel):
    status: MaintenanceStatus
    notes: Optional[str] = None
