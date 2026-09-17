import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Text, JSON
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin

class MaintenanceStatus(str, enum.Enum):
    OPEN = "OPEN"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    REPAIR_COMPLETED = "REPAIR_COMPLETED"
    VERIFIED = "VERIFIED"
    CLOSED = "CLOSED"

class MaintenancePriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class MaintenanceTask(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "maintenance_tasks"
    task_ref = Column(String, unique=True, nullable=False, index=True)  # MT-2048
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=False, index=True)
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    status = Column(Enum(MaintenanceStatus), default=MaintenanceStatus.OPEN, nullable=False)
    priority = Column(Enum(MaintenancePriority), default=MaintenancePriority.MEDIUM, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verified_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    incident = relationship("Incident", back_populates="maintenance_tasks")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    verified_by = relationship("User", foreign_keys=[verified_by_id])
    logs = relationship("MaintenanceLog", back_populates="task", cascade="all, delete-orphan")

class MaintenanceLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "maintenance_logs"
    task_id = Column(UUID(as_uuid=True), ForeignKey("maintenance_tasks.id"), nullable=False, index=True)
    logged_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    note = Column(Text, nullable=True)
    attachments = Column(JSON, nullable=True)  # List of image URLs
    action_taken = Column(String, nullable=True)

    task = relationship("MaintenanceTask", back_populates="logs")
    logged_by = relationship("User")
