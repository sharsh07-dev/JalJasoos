"""Pydantic schemas for Node and Device models."""
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.device import NodeStatus, ValveStatus


class NodeCreate(BaseModel):
    node_id: str
    serial_number: Optional[str] = None
    zone_id: UUID
    firmware_version: Optional[str] = None
    hardware_version: Optional[str] = None


class NodeOut(NodeCreate):
    id: UUID
    status: NodeStatus
    last_seen: Optional[datetime] = None
    battery_percent: Optional[int] = None
    rssi_dbm: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NodeStatusUpdate(BaseModel):
    status: NodeStatus


class ValveOut(BaseModel):
    id: UUID
    node_id: UUID
    label: str
    status: ValveStatus
    last_command_at: Optional[datetime] = None
    last_confirmed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
