"""Buildings CRUD router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.infrastructure import Building
from app.schemas.infrastructure import BuildingCreate, BuildingOut
from app.core.security import get_current_user, require_roles
from app.models.user import UserRole

router = APIRouter()

@router.get("/", response_model=List[BuildingOut])
def list_buildings(society_id: str = None, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    q = db.query(Building)
    if society_id:
        q = q.filter(Building.society_id == society_id)
    elif current_user.role.name != UserRole.SUPER_ADMIN and current_user.society_id:
        q = q.filter(Building.society_id == current_user.society_id)
    return q.all()

@router.post("/", response_model=BuildingOut, status_code=status.HTTP_201_CREATED)
def create_building(
    payload: BuildingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.FACILITY_MANAGER)),
):
    building = Building(**payload.model_dump())
    db.add(building)
    db.commit()
    db.refresh(building)
    return building

@router.get("/{building_id}", response_model=BuildingOut)
def get_building(building_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    building = db.query(Building).filter(Building.id == building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    return building
