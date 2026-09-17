import enum
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum, Integer, Boolean
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin

class ValveAction(str, enum.Enum):
    OPEN = "OPEN"
    CLOSE = "CLOSE"
    STOP = "STOP"
    PARTIAL = "PARTIAL"

class CommandStatus(str, enum.Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    RECEIVED = "RECEIVED"
    ACTUATION_STARTED = "ACTUATION_STARTED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"

class ValveCommand(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "valve_commands"
    valve_id = Column(UUID(as_uuid=True), ForeignKey("valves.id"), nullable=False, index=True)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=True)
    action = Column(Enum(ValveAction), nullable=False)
    status = Column(Enum(CommandStatus), default=CommandStatus.PENDING, nullable=False)
    issued_by = Column(String, nullable=False)  # EDGE_GATEWAY, USER:uuid, SYSTEM
    sent_at = Column(DateTime(timezone=True), nullable=True)
    received_at = Column(DateTime(timezone=True), nullable=True)
    actuation_started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    command_latency_ms = Column(Float, nullable=True)
    actuation_time_ms = Column(Float, nullable=True)
    confirmation_time_ms = Column(Float, nullable=True)
    retry_count = Column(Integer, default=0)
    failure_reason = Column(String, nullable=True)

    valve = relationship("Valve", back_populates="commands")

class ValveSchedule(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "valve_schedules"
    valve_id = Column(UUID(as_uuid=True), ForeignKey("valves.id"), nullable=False, index=True)
    action = Column(Enum(ValveAction), nullable=False)
    cron_expression = Column(String, nullable=False) # e.g. "0 22 * * *" for 10 PM
    is_active = Column(Boolean, default=True)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    valve = relationship("Valve")
