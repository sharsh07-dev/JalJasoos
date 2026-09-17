import enum
from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin

class Society(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "societies"
    name = Column(String, nullable=False)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    pincode = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)

    buildings = relationship("Building", back_populates="society", cascade="all, delete-orphan")
    users = relationship("User", back_populates="society")

class Building(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "buildings"
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)  # e.g. "A", "B"
    society_id = Column(UUID(as_uuid=True), ForeignKey("societies.id"), nullable=False, index=True)
    total_floors = Column(Integer, nullable=False, default=1)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    society = relationship("Society", back_populates="buildings")
    floors = relationship("Floor", back_populates="building", cascade="all, delete-orphan")

class Floor(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "floors"
    number = Column(Integer, nullable=False)
    label = Column(String, nullable=True)  # e.g. "Ground Floor"
    building_id = Column(UUID(as_uuid=True), ForeignKey("buildings.id"), nullable=False, index=True)

    building = relationship("Building", back_populates="floors")
    zones = relationship("Zone", back_populates="floor", cascade="all, delete-orphan")

class Zone(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "zones"
    name = Column(String, nullable=False)  # e.g. "North Riser"
    code = Column(String, nullable=False)
    floor_id = Column(UUID(as_uuid=True), ForeignKey("floors.id"), nullable=False, index=True)
    description = Column(String, nullable=True)

    floor = relationship("Floor", back_populates="zones")
    nodes = relationship("Node", back_populates="zone", cascade="all, delete-orphan")
