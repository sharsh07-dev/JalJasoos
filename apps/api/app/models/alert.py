import enum
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum, JSON
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin

class AlertSeverity(str, enum.Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class Alert(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "alerts"
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=True, index=True)
    node_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id"), nullable=True, index=True)
    severity = Column(Enum(AlertSeverity), nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    event_metadata = Column(JSON, nullable=True)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

class Notification(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "notifications"
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    alert_id = Column(UUID(as_uuid=True), ForeignKey("alerts.id"), nullable=True)
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    channel = Column(String, default="IN_APP")  # IN_APP, EMAIL, PUSH
    user = relationship("User")
