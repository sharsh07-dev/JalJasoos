"""Zones CRUD router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.infrastructure import Zone
from app.schemas.infrastructure import ZoneCreate, ZoneOut
from app.core.security import get_current_user, require_roles
from app.models.user import UserRole

router = APIRouter()

@router.get("/", response_model=List[ZoneOut])
def list_zones(floor_id: str = None, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    q = db.query(Zone)
    if floor_id:
        q = q.filter(Zone.floor_id == floor_id)
    return q.all()

@router.post("/", response_model=ZoneOut, status_code=status.HTTP_201_CREATED)
def create_zone(
    payload: ZoneCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.FACILITY_MANAGER)),
):
    zone = Zone(**payload.model_dump())
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone

@router.get("/{zone_id}", response_model=ZoneOut)
def get_zone(zone_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    return zone
