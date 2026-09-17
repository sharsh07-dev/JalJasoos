from sqlalchemy import Column, String, JSON, Boolean
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin

class SystemSetting(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "system_settings"
    key = Column(String, unique=True, nullable=False)
    value = Column(JSON, nullable=True)
    description = Column(String, nullable=True)
    is_sensitive = Column(Boolean, default=False)  # If True, never return in API
