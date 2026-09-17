"""Authentication Router — login, refresh, logout, /me."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
)
from app.schemas.auth import TokenResponse, RefreshRequest, UserOut
from app.models.audit import AuditLog

router = APIRouter()


def _record_audit(db: Session, action: str, user_id=None, request: Request = None, result: str = "SUCCESS"):
    log = AuditLog(
        user_id=user_id,
        timestamp=datetime.now(timezone.utc),
        action=action,
        resource_type="auth",
        ip_address=request.client.host if request and request.client else None,
        result=result,
    )
    db.add(log)
    db.commit()


@router.post("/login", response_model=TokenResponse)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        _record_audit(db, "auth.login", result="FAILURE", request=request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is disabled")

    token_data = {"sub": str(user.id), "role": user.role.name.value}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    _record_audit(db, "auth.login", user_id=user.id, request=request)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        role=user.role.name.value,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    payload = decode_token(body.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    token_data = {"sub": str(user.id), "role": user.role.name.value}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        role=user.role.name.value,
    )


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return UserOut(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.name.value,
        is_active=current_user.is_active,
    )
