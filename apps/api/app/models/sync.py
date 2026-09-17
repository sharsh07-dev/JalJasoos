import enum
from sqlalchemy import Column, String, Integer, DateTime, Enum, JSON
from sqlalchemy import Uuid as UUID
from app.database import Base
from app.models.base import UUIDMixin

class SyncStatus(str, enum.Enum):
    PENDING = "PENDING"
    SYNCING = "SYNCING"
    SYNCED = "SYNCED"
    FAILED = "FAILED"
    DEAD_LETTER = "DEAD_LETTER"

class EdgeSyncQueue(Base, UUIDMixin):
    """Holds events queued by the edge gateway for cloud synchronization."""
    __tablename__ = "edge_sync_queue"
    event_type = Column(String, nullable=False, index=True)
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    retry_count = Column(Integer, default=0, nullable=False)
    last_attempt = Column(DateTime(timezone=True), nullable=True)
    sync_status = Column(Enum(SyncStatus), default=SyncStatus.PENDING, nullable=False, index=True)
    error_message = Column(String, nullable=True)
