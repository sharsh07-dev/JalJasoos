"""Societies CRUD router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.infrastructure import Society
from app.schemas.infrastructure import SocietyCreate, SocietyOut
from app.core.security import get_current_user, require_roles
from app.models.user import UserRole

router = APIRouter()

@router.get("/", response_model=List[SocietyOut])
def list_societies(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role.name == UserRole.SUPER_ADMIN:
        return db.query(Society).all()
    if current_user.society_id:
        return db.query(Society).filter(Society.id == current_user.society_id).all()
    return []

@router.post("/", response_model=SocietyOut, status_code=status.HTTP_201_CREATED)
def create_society(
    payload: SocietyCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN)),
):
    society = Society(**payload.model_dump())
    db.add(society)
    db.commit()
    db.refresh(society)
    return society

@router.get("/{society_id}", response_model=SocietyOut)
def get_society(society_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    society = db.query(Society).filter(Society.id == society_id).first()
    if not society:
        raise HTTPException(status_code=404, detail="Society not found")
    if current_user.role.name != UserRole.SUPER_ADMIN and str(current_user.society_id) != society_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return society

@router.delete("/{society_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_society(
    society_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN)),
):
    society = db.query(Society).filter(Society.id == society_id).first()
    if not society:
        raise HTTPException(status_code=404, detail="Society not found")
    db.delete(society)
    db.commit()
