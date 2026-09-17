import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, Integer, JSON, Enum
from sqlalchemy import Uuid as UUID
from app.database import Base

class EdgeTelemetry(Base):
    __tablename__ = "telemetry"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    node_id = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), index=True, nullable=False)
    flow_lpm = Column(Float)
    pressure_bar = Column(Float)
    acoustic_rms = Column(Float)
    pump_state = Column(Boolean)
    is_anomaly = Column(Boolean, default=False)
    synced_to_cloud = Column(Boolean, default=False)

class EdgeIncident(Base):
    __tablename__ = "incidents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_ref = Column(String, unique=True, nullable=False)
    node_id = Column(String, index=True, nullable=False)
    status = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    ai_confidence = Column(Float, nullable=True)
    detection_time = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    synced_to_cloud = Column(Boolean, default=False)

class EdgeSyncQueue(Base):
    __tablename__ = "edge_sync_queue"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    sync_status = Column(String, default="PENDING")
    retry_count = Column(Integer, default=0)
