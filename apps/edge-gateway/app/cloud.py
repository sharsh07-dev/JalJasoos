import asyncio
import json
import websockets
import httpx
import structlog
from datetime import datetime, timezone
import paho.mqtt.client as mqtt

from app.config import settings
from app.database import SessionLocal
from app.models import EdgeSyncQueue, EdgeTelemetry

logger = structlog.get_logger()

async def sync_telemetry_loop():
    """Batch and send locally buffered telemetry to the cloud"""
    while True:
        try:
            with SessionLocal() as db:
                unsynced = db.query(EdgeTelemetry).filter(EdgeTelemetry.synced_to_cloud == False).limit(50).all()
                if not unsynced:
                    await asyncio.sleep(5)
                    continue

                payload = []
                for t in unsynced:
                    payload.append({
                        "node_id": t.node_id,
                        "timestamp": t.timestamp.isoformat(),
                        "flow_lpm": t.flow_lpm,
                        "pressure_bar": t.pressure_bar,
                        "acoustic_rms": t.acoustic_rms,
                        "pump_state": t.pump_state
                    })
                
                # Mock push to cloud
                async with httpx.AsyncClient() as client:
                    resp = await client.post(
                        f"{settings.CLOUD_API_URL}/api/v1/telemetry/batch",
                        json={"batch": payload},
                        headers={"Authorization": f"Bearer {settings.EDGE_API_KEY}"}
                    )
                    
                    if resp.status_code in (200, 201):
                        for t in unsynced:
                            t.synced_to_cloud = True
                        db.commit()
                        logger.debug("Synced telemetry batch to cloud", count=len(unsynced))
                    else:
                        logger.warning("Cloud telemetry sync failed", status=resp.status_code)
                        await asyncio.sleep(10)
        except Exception as e:
            logger.error("Telemetry sync error", error=str(e))
            await asyncio.sleep(10)

async def cloud_websocket_bridge(mqtt_client: mqtt.Client):
    """
    Maintains a persistent outbound WebSocket connection to the Cloud.
    Receives valve commands from Cloud and forwards them to local Mosquitto.
    This architecture bypasses residential NAT/firewalls.
    """
    ws_url = f"{settings.CLOUD_WS_URL}/api/v1/system/edge-bridge"
    while True:
        try:
            logger.info("Connecting to Cloud WebSocket", url=ws_url)
            async with websockets.connect(ws_url) as ws:
                logger.info("Cloud WebSocket connected")
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    if data.get("type") == "VALVE_COMMAND":
                        node_id = data["node_id"]
                        cmd_topic = f"jaljasoos/{settings.SOCIETY_ID}/{settings.BUILDING_ID}/+/+/{node_id}/command"
                        # Use a wildcard for zone/building if not provided, or strict if provided
                        
                        cmd_payload = {
                            "command_id": data["command_id"],
                            "action": data["action"],
                            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                            "issuer": "CLOUD_MANUAL",
                            "timeout_ms": 15000
                        }
                        mqtt_client.publish(cmd_topic, json.dumps(cmd_payload), qos=2)
                        logger.info("Forwarded cloud command to edge MQTT", node_id=node_id, action=data["action"])
                        
        except Exception as e:
            logger.error("Cloud WebSocket disconnected", error=str(e))
            await asyncio.sleep(5)
