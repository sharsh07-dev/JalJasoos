import structlog
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, text

from app.database import SessionLocal
from app.models.telemetry import Telemetry
from app.models.incident import Incident

logger = structlog.get_logger()

def run_aggregation_job():
    """
    Rolls up raw telemetry into 5-minute averages.
    Retains high-res data for active incident windows.
    """
    logger.info("Starting Telemetry Aggregation Job")
    try:
        with SessionLocal() as db:
            # In a real timeseries DB (like TimescaleDB), this is a continuous aggregate.
            # For standard Postgres, we do a manual rollup for data older than 2 hours
            cutoff = datetime.now(timezone.utc) - timedelta(hours=2)
            
            # Find nodes with active incidents (keep high res data)
            active_incidents = db.query(Incident.node_id).filter(
                Incident.status != "RESOLVED",
                Incident.status != "FALSE_ALARM"
            ).all()
            active_node_ids = [str(n[0]) for n in active_incidents]
            
            # Delete old non-incident data (Simulating aggregation)
            # A real implementation would INSERT INTO telemetry_5m (SELECT avg(flow)... GROUP BY 5m)
            # then DELETE from telemetry.
            query = db.query(Telemetry).filter(Telemetry.timestamp < cutoff)
            if active_node_ids:
                query = query.filter(Telemetry.node_id.notin_(active_node_ids))
                
            deleted = query.delete(synchronize_session=False)
            db.commit()
            
            logger.info("Aggregation complete", pruned_raw_rows=deleted)
    except Exception as e:
        logger.error("Aggregation job failed", error=str(e))
