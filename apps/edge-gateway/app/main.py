from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
import structlog
import threading

from app.config import settings
from app.database import engine, Base
from app.mqtt_worker import start_mqtt_worker
from app.cloud import sync_telemetry_loop, cloud_websocket_bridge

logger = structlog.get_logger()

# Shared state
gateway_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("JalJasoos Edge Gateway Starting...")
    
    # Create local DB tables
    Base.metadata.create_all(bind=engine)
    
    
    # Start MQTT Worker in a background thread (paho-mqtt loop)
    mqtt_client = start_mqtt_worker()
    gateway_state["mqtt_client"] = mqtt_client
    
    # Start Cloud Sync tasks in asyncio loop
    task1 = asyncio.create_task(sync_telemetry_loop())
    task2 = asyncio.create_task(cloud_websocket_bridge(mqtt_client))
    
    yield
    
    logger.info("Shutting down Edge Gateway...")
    task1.cancel()
    task2.cancel()
    mqtt_client.loop_stop()

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "mqtt_connected": gateway_state.get("mqtt_client").is_connected() if gateway_state.get("mqtt_client") else False
    }

@app.get("/api/local/status")
def get_local_status():
    """Local network API for edge dashboard"""
    return {
        "society_id": settings.SOCIETY_ID,
        "mode": "OFFLINE_FIRST",
        "ai_model": "PINN_EDGE_v1.0 (Calibrated)",
    }
