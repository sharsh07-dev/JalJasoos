import uuid
import enum
from sqlalchemy import Column, String, Boolean, Enum, ForeignKey
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin

class UserRole(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    FACILITY_MANAGER = "FACILITY_MANAGER"
    MAINTENANCE_STAFF = "MAINTENANCE_STAFF"
    RESIDENT = "RESIDENT"

class Role(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "roles"
    name = Column(Enum(UserRole), unique=True, nullable=False)
    description = Column(String, nullable=True)
    users = relationship("User", back_populates="role")

class Permission(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "permissions"
    role_name = Column(Enum(UserRole), nullable=False)
    resource = Column(String, nullable=False)
    action = Column(String, nullable=False)  # read, write, delete, command

class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    society_id = Column(UUID(as_uuid=True), ForeignKey("societies.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    role = relationship("Role", back_populates="users")
    society = relationship("Society", back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user")
