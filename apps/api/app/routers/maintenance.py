"""Maintenance tasks and logs router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
import uuid

from app.database import get_db
from app.models.maintenance import MaintenanceTask, MaintenanceLog, MaintenanceStatus
from app.schemas.maintenance import (
    MaintenanceTaskCreate, MaintenanceTaskOut,
    MaintenanceLogCreate, MaintenanceLogOut,
    MaintenanceTaskStatusUpdate,
)
from app.core.security import get_current_user, require_roles
from app.models.user import UserRole

router = APIRouter()

def _generate_task_ref(db: Session) -> str:
    count = db.query(MaintenanceTask).count()
    return f"MT-{count + 1:04d}"

@router.get("/", response_model=List[MaintenanceTaskOut])
def list_tasks(
    status_filter: Optional[MaintenanceStatus] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    q = db.query(MaintenanceTask)
    if status_filter:
        q = q.filter(MaintenanceTask.status == status_filter)
    if current_user.role.name == UserRole.MAINTENANCE_STAFF:
        q = q.filter(MaintenanceTask.assigned_to_id == current_user.id)
    return q.order_by(MaintenanceTask.created_at.desc()).all()

@router.post("/", response_model=MaintenanceTaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: MaintenanceTaskCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.FACILITY_MANAGER)),
):
    task = MaintenanceTask(
        task_ref=_generate_task_ref(db),
        **payload.model_dump(),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.get("/{task_ref}", response_model=MaintenanceTaskOut)
def get_task(task_ref: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    task = db.query(MaintenanceTask).filter(MaintenanceTask.task_ref == task_ref).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/{task_ref}/status")
def update_task_status(
    task_ref: str,
    body: MaintenanceTaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.services.incident_engine import IncidentEngine
    from app.models.incident import IncidentStatus

    task = db.query(MaintenanceTask).filter(MaintenanceTask.task_ref == task_ref).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    task.status = body.status
    now = datetime.now(timezone.utc)
    
    if body.status == MaintenanceStatus.REPAIR_COMPLETED:
        task.completed_at = now
        if task.incident:
            IncidentEngine._add_event(
                db, 
                task.incident, 
                IncidentStatus.REPAIR_COMPLETED,
                f"Repair completed by technician: {current_user.email}",
                "USER",
                str(current_user.id)
            )
            
    if body.status == MaintenanceStatus.VERIFIED:
        task.verified_at = now
        task.verified_by_id = current_user.id
        if task.incident:
            task.incident.resolution_time = now
            IncidentEngine._add_event(
                db, 
                task.incident, 
                IncidentStatus.RESOLVED,
                f"Repair verified and incident resolved by {current_user.email}",
                "USER",
                str(current_user.id)
            )
            
    db.commit()
    return {"status": "updated", "new_status": body.status.value}

@router.post("/{task_ref}/logs", response_model=MaintenanceLogOut, status_code=status.HTTP_201_CREATED)
def add_log(
    task_ref: str,
    body: MaintenanceLogCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    task = db.query(MaintenanceTask).filter(MaintenanceTask.task_ref == task_ref).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    log = MaintenanceLog(
        task_id=task.id,
        logged_by_id=current_user.id,
        **body.model_dump(),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

@router.get("/{task_ref}/logs", response_model=List[MaintenanceLogOut])
def get_logs(task_ref: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    task = db.query(MaintenanceTask).filter(MaintenanceTask.task_ref == task_ref).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.logs
