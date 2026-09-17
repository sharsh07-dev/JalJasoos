from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUIDMixin

class AuditLog(Base, UUIDMixin):
    __tablename__ = "audit_logs"
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    action = Column(String, nullable=False)  # e.g. valve.close, incident.acknowledge
    resource_type = Column(String, nullable=True)  # valve, incident, user
    resource_id = Column(String, nullable=True)  # UUID as string
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    result = Column(String, nullable=False, default="SUCCESS")  # SUCCESS, FAILURE
    event_metadata = Column(JSON, nullable=True)

    user = relationship("User", back_populates="audit_logs")
