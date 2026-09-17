import enum
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin

class NodeStatus(str, enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    DEGRADED = "DEGRADED"
    MAINTENANCE = "MAINTENANCE"
    DECOMMISSIONED = "DECOMMISSIONED"

class ValveStatus(str, enum.Enum):
    OPEN = "OPEN"
    CLOSING = "CLOSING"
    CLOSED = "CLOSED"
    OPENING = "OPENING"
    FAULT = "FAULT"
    UNKNOWN = "UNKNOWN"

class Node(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "nodes"
    node_id = Column(String, unique=True, nullable=False, index=True)  # Human-readable e.g. NODE-A3-04
    serial_number = Column(String, unique=True, nullable=True)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("zones.id"), nullable=False, index=True)
    firmware_version = Column(String, nullable=True)
    hardware_version = Column(String, nullable=True)
    last_seen = Column(DateTime(timezone=True), nullable=True)
    battery_percent = Column(Integer, nullable=True)
    rssi_dbm = Column(Integer, nullable=True)
    status = Column(Enum(NodeStatus), default=NodeStatus.OFFLINE, nullable=False)
    installation_date = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    zone = relationship("Zone", back_populates="nodes")
    sensors = relationship("Sensor", back_populates="node", cascade="all, delete-orphan")
    valves = relationship("Valve", back_populates="node", cascade="all, delete-orphan")
    telemetry = relationship("Telemetry", back_populates="node")
    incidents = relationship("Incident", back_populates="node")
    health_records = relationship("DeviceHealth", back_populates="node")

class SensorType(str, enum.Enum):
    FLOW = "FLOW"
    PRESSURE = "PRESSURE"
    ACOUSTIC = "ACOUSTIC"
    TANK_LEVEL = "TANK_LEVEL"
    MOTOR_CURRENT = "MOTOR_CURRENT"
    PUMP_STATE = "PUMP_STATE"

class Sensor(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "sensors"
    node_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id"), nullable=False, index=True)
    sensor_type = Column(Enum(SensorType), nullable=False)
    unit = Column(String, nullable=True)
    calibration_offset = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    node = relationship("Node", back_populates="sensors")

class Valve(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "valves"
    node_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id"), nullable=False, index=True)
    label = Column(String, nullable=False)  # e.g. "Main Isolation Valve"
    status = Column(Enum(ValveStatus), default=ValveStatus.UNKNOWN, nullable=False)
    last_command_at = Column(DateTime(timezone=True), nullable=True)
    last_confirmed_at = Column(DateTime(timezone=True), nullable=True)
    node = relationship("Node", back_populates="valves")
    commands = relationship("ValveCommand", back_populates="valve")

class PumpStatus(str, enum.Enum):
    ON = "ON"
    OFF = "OFF"
    FAULT = "FAULT"
    UNKNOWN = "UNKNOWN"

class Pump(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "pumps"
    label = Column(String, nullable=False)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("zones.id"), nullable=True)
    status = Column(Enum(PumpStatus), default=PumpStatus.UNKNOWN)
    rated_current_a = Column(Float, nullable=True)
    rated_flow_lpm = Column(Float, nullable=True)
    zone = relationship("Zone")

class Tank(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "tanks"
    label = Column(String, nullable=False)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("zones.id"), nullable=True)
    capacity_liters = Column(Float, nullable=True)
    zone = relationship("Zone")
