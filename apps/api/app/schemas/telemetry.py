"""Pydantic schemas for Telemetry."""
from pydantic import BaseModel, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime


class TelemetryIngest(BaseModel):
    """Schema for MQTT payload ingestion from ESP32 or edge gateway."""
    node_id: str
    timestamp: datetime
    flow_lpm: Optional[float] = None
    pressure_bar: Optional[float] = None
    acoustic_rms: Optional[float] = None
    pump_state: Optional[bool] = None
    tank_level_percent: Optional[float] = None
    motor_current_a: Optional[float] = None
    battery_percent: Optional[int] = None
    signal_rssi: Optional[int] = None

    @field_validator("flow_lpm")
    @classmethod
    def flow_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError("flow_lpm must be non-negative")
        return v

    @field_validator("pressure_bar")
    @classmethod
    def pressure_reasonable(cls, v):
        if v is not None and (v < 0 or v > 20):
            raise ValueError("pressure_bar must be between 0 and 20")
        return v

    @field_validator("tank_level_percent")
    @classmethod
    def tank_level_range(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError("tank_level_percent must be 0-100")
        return v

    @field_validator("battery_percent")
    @classmethod
    def battery_range(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError("battery_percent must be 0-100")
        return v


class TelemetryOut(BaseModel):
    id: UUID
    node_id: UUID
    timestamp: datetime
    ingested_at: datetime
    flow_lpm: Optional[float] = None
    pressure_bar: Optional[float] = None
    acoustic_rms: Optional[float] = None
    pump_state: Optional[bool] = None
    tank_level_percent: Optional[float] = None
    motor_current_a: Optional[float] = None
    battery_percent: Optional[int] = None
    signal_rssi: Optional[int] = None
    is_anomaly: bool
    source: str

    class Config:
        from_attributes = True

class BatchTelemetryIngest(BaseModel):
    batch: list[TelemetryIngest]
