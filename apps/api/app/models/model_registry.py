import enum
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum, JSON, Boolean
from sqlalchemy import Uuid as UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin

class ModelType(str, enum.Enum):
    PINN = "PINN"
    FUSION = "FUSION"
    THRESHOLD = "THRESHOLD"

class ModelVersion(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "model_versions"
    name = Column(String, nullable=False)
    model_type = Column(Enum(ModelType), nullable=False)
    version = Column(String, nullable=False)
    file_path = Column(String, nullable=True)
    is_active = Column(Boolean, default=False)
    training_notes = Column(String, nullable=True)
    metrics = Column(JSON, nullable=True)
    deployed_at = Column(DateTime(timezone=True), nullable=True)
    deployed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    predictions = relationship("ModelPrediction", back_populates="model_version")

class ModelPrediction(Base, UUIDMixin):
    __tablename__ = "model_predictions"
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=False, index=True)
    model_version_id = Column(UUID(as_uuid=True), ForeignKey("model_versions.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    raw_score = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)  # 0.0 to 1.0 ONLY from real model
    prediction_label = Column(String, nullable=True)  # LEAK, NO_LEAK
    features_used = Column(JSON, nullable=True)
    inference_time_ms = Column(Float, nullable=True)

    incident = relationship("Incident", back_populates="predictions")
    model_version = relationship("ModelVersion", back_populates="predictions")
