from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUIDMixin

class DeviceHealth(Base, UUIDMixin):
    __tablename__ = "device_health"
    node_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    uptime_seconds = Column(Integer, nullable=True)
    free_heap_bytes = Column(Integer, nullable=True)
    wifi_rssi = Column(Integer, nullable=True)
    mqtt_reconnects = Column(Integer, nullable=True)
    battery_percent = Column(Integer, nullable=True)
    cpu_temp_c = Column(Float, nullable=True)

    node = relationship("Node", back_populates="health_records")
