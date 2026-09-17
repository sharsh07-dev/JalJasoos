"""Pydantic schemas for infrastructure models."""
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


# ── Society ──────────────────────────────────────────────────────────────────
class SocietyCreate(BaseModel):
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None


class SocietyOut(SocietyCreate):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ── Building ──────────────────────────────────────────────────────────────────
class BuildingCreate(BaseModel):
    name: str
    code: str
    society_id: UUID
    total_floors: int = 1
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class BuildingOut(BuildingCreate):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ── Floor ──────────────────────────────────────────────────────────────────
class FloorCreate(BaseModel):
    number: int
    label: Optional[str] = None
    building_id: UUID


class FloorOut(FloorCreate):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ── Zone ──────────────────────────────────────────────────────────────────
class ZoneCreate(BaseModel):
    name: str
    code: str
    floor_id: UUID
    description: Optional[str] = None


class ZoneOut(ZoneCreate):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
