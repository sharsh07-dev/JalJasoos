import enum
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum, JSON
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin

class IncidentStatus(str, enum.Enum):
    NORMAL = "NORMAL"
    ANOMALY_DETECTED = "ANOMALY_DETECTED"
    MULTI_SENSOR_VERIFICATION = "MULTI_SENSOR_VERIFICATION"
    LEAK_SUSPECTED = "LEAK_SUSPECTED"
    LEAK_CONFIRMED = "LEAK_CONFIRMED"
    ZONE_LOCALIZED = "ZONE_LOCALIZED"
    AUTOMATED_ISOLATION = "AUTOMATED_ISOLATION"
    MAINTENANCE_ASSIGNED = "MAINTENANCE_ASSIGNED"
    REPAIR_COMPLETED = "REPAIR_COMPLETED"
    POST_REPAIR_VERIFICATION = "POST_REPAIR_VERIFICATION"
    RESOLVED = "RESOLVED"
    FALSE_ALARM = "FALSE_ALARM"

class IncidentSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class Incident(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "incidents"
    incident_ref = Column(String, unique=True, nullable=False, index=True)  # INC-0001
    node_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id"), nullable=False, index=True)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.ANOMALY_DETECTED, nullable=False)
    severity = Column(Enum(IncidentSeverity), default=IncidentSeverity.MEDIUM, nullable=False)
    detection_time = Column(DateTime(timezone=True), nullable=False)
    localization_time = Column(DateTime(timezone=True), nullable=True)
    isolation_time = Column(DateTime(timezone=True), nullable=True)
    resolution_time = Column(DateTime(timezone=True), nullable=True)
    flow_at_detection = Column(Float, nullable=True)
    pressure_at_detection = Column(Float, nullable=True)
    acoustic_at_detection = Column(Float, nullable=True)
    ai_confidence = Column(Float, nullable=True)  # NULL = model not calibrated
    estimated_loss_liters = Column(Float, nullable=True)
    acknowledged_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    notes = Column(String, nullable=True)

    node = relationship("Node", back_populates="incidents")
    events = relationship("IncidentEvent", back_populates="incident", order_by="IncidentEvent.timestamp", cascade="all, delete-orphan")
    maintenance_tasks = relationship("MaintenanceTask", back_populates="incident", cascade="all, delete-orphan")
    predictions = relationship("ModelPrediction", back_populates="incident")

class IncidentEvent(Base, UUIDMixin):
    """Immutable event log for every state transition in an incident."""
    __tablename__ = "incident_events"
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    from_status = Column(Enum(IncidentStatus), nullable=True)
    to_status = Column(Enum(IncidentStatus), nullable=False)
    triggered_by = Column(String, nullable=False)  # SYSTEM, USER, EDGE_GATEWAY
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    message = Column(String, nullable=False)
    event_metadata = Column(JSON, nullable=True)

    incident = relationship("Incident", back_populates="events")
