"""Valve command router — human override path."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List

from app.database import get_db
from app.models.device import Valve, ValveStatus
from app.models.command import ValveCommand, CommandStatus
from app.schemas.valve import ValveCommandCreate, ValveCommandOut
from app.core.security import get_current_user, require_roles
from app.models.user import UserRole
from app.models.audit import AuditLog

router = APIRouter()

@router.post("/{valve_id}/command", response_model=ValveCommandOut, status_code=status.HTTP_202_ACCEPTED)
def issue_valve_command(
    valve_id: str,
    payload: ValveCommandCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.FACILITY_MANAGER)),
):
    """Issue a valve command. The edge gateway will pick this up and actuate."""
    valve = db.query(Valve).filter(Valve.id == valve_id).first()
    if not valve:
        raise HTTPException(status_code=404, detail="Valve not found")

    command = ValveCommand(
        valve_id=valve.id,
        incident_id=payload.incident_id,
        action=payload.action,
        status=CommandStatus.PENDING,
        issued_by=f"USER:{current_user.id}",
    )
    db.add(command)

    # Record audit log
    log = AuditLog(
        user_id=current_user.id,
        timestamp=datetime.now(timezone.utc),
        action=f"valve.{payload.action.value.lower()}",
        resource_type="valve",
        resource_id=str(valve_id),
        result="SUCCESS",
        event_metadata={"incident_id": str(payload.incident_id) if payload.incident_id else None},
    )
    db.add(log)
    db.commit()
    db.refresh(command)

    # Trigger async push to edge via WebSocket
    import asyncio
    from app.core.ws_manager import edge_bridge_manager
    # We assume building -> society is linked, for now just use "society01"
    society_id = "society01" 
    
    cmd_msg = {
        "command_id": str(command.id),
        "node_id": valve.node.node_id if hasattr(valve, "node") else str(valve.node_id),
        "action": payload.action.value
    }
    
    # We can't await inside sync route easily if we don't have async def,
    # wait, the route is sync. So we run it in the existing event loop.
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(edge_bridge_manager.send_valve_command(society_id, cmd_msg))
    except Exception as e:
        logger.error("Failed to push command to Edge WebSocket", error=str(e))

    return command

@router.get("/{valve_id}/commands", response_model=List[ValveCommandOut])
def get_valve_commands(
    valve_id: str,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    valve = db.query(Valve).filter(Valve.id == valve_id).first()
    if not valve:
        raise HTTPException(status_code=404, detail="Valve not found")
    return db.query(ValveCommand).filter(ValveCommand.valve_id == valve.id).order_by(ValveCommand.created_at.desc()).limit(limit).all()

@router.post("/{valve_id}/ack")
def valve_ack(
    valve_id: str,
    command_id: str,
    valve_status: ValveStatus,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Receive valve actuation acknowledgement from edge gateway."""
    command = db.query(ValveCommand).filter(
        ValveCommand.id == command_id,
        ValveCommand.valve_id == valve_id,
    ).first()
    if not command:
        raise HTTPException(status_code=404, detail="Command not found")

    now = datetime.now(timezone.utc)
    command.completed_at = now
    command.status = CommandStatus.COMPLETED

    if command.sent_at:
        command.confirmation_time_ms = (now - command.sent_at).total_seconds() * 1000

    valve = db.query(Valve).filter(Valve.id == valve_id).first()
    valve.status = valve_status
    valve.last_confirmed_at = now

    db.commit()
    return {"status": "acknowledged", "valve_status": valve_status.value}

from app.models.command import ValveSchedule
from app.schemas.valve import ValveScheduleCreate, ValveScheduleOut

@router.post("/{valve_id}/schedule", response_model=ValveScheduleOut, status_code=status.HTTP_201_CREATED)
def create_valve_schedule(
    valve_id: str,
    payload: ValveScheduleCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.FACILITY_MANAGER)),
):
    """Create a recurring cron schedule for a valve."""
    valve = db.query(Valve).filter(Valve.id == valve_id).first()
    if not valve:
        raise HTTPException(status_code=404, detail="Valve not found")
        
    schedule = ValveSchedule(
        valve_id=valve.id,
        action=payload.action,
        cron_expression=payload.cron_expression,
        is_active=True,
        created_by_id=current_user.id
    )
    
    db.add(schedule)
    
    # Audit log
    log = AuditLog(
        user_id=current_user.id,
        timestamp=datetime.now(timezone.utc),
        action="valve.schedule.create",
        resource_type="valve",
        resource_id=str(valve_id),
        result="SUCCESS",
        event_metadata={"action": payload.action.value, "cron": payload.cron_expression}
    )
    db.add(log)
    db.commit()
    db.refresh(schedule)
    return schedule

@router.get("/{valve_id}/schedules", response_model=List[ValveScheduleOut])
def get_valve_schedules(
    valve_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all active schedules for a valve."""
    return db.query(ValveSchedule).filter(ValveSchedule.valve_id == valve_id).all()
