"""Alerts and notifications router."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.alert import Alert, Notification
from app.core.security import get_current_user

router = APIRouter()

@router.get("/")
def list_alerts(limit: int = 50, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(Alert).order_by(Alert.created_at.desc()).limit(limit).all()

@router.get("/my-notifications")
def my_notifications(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )

@router.post("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from datetime import datetime, timezone
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    notif.read_at = datetime.now(timezone.utc)
    db.commit()
    return {"status": "read"}
