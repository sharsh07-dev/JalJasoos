from datetime import datetime
from sqlalchemy import Column, Float, Integer, Boolean, DateTime, String, ForeignKey, Index
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUIDMixin

class Telemetry(Base, UUIDMixin):
    __tablename__ = "telemetry"
    __table_args__ = (
        Index("ix_telemetry_node_id_timestamp", "node_id", "timestamp"),
    )
    node_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)  # Device timestamp
    ingested_at = Column(DateTime(timezone=True), nullable=False)  # Server ingestion timestamp
    flow_lpm = Column(Float, nullable=True)
    pressure_bar = Column(Float, nullable=True)
    acoustic_rms = Column(Float, nullable=True)
    pump_state = Column(Boolean, nullable=True)
    tank_level_percent = Column(Float, nullable=True)
    motor_current_a = Column(Float, nullable=True)
    battery_percent = Column(Integer, nullable=True)
    signal_rssi = Column(Integer, nullable=True)
    is_anomaly = Column(Boolean, default=False, nullable=False)
    source = Column(String, default="DEVICE", nullable=False)  # DEVICE, SIMULATOR

    node = relationship("Node", back_populates="telemetry")
