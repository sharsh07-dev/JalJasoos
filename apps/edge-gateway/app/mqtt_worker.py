import time
import json
import uuid
from datetime import datetime, timezone
import paho.mqtt.client as mqtt
import structlog
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models import EdgeTelemetry, EdgeIncident, EdgeSyncQueue
from app.ai import ai_engine
from jaljasoos_mqtt_contracts import parse_topic, validate_telemetry

logger = structlog.get_logger()

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        logger.info("Edge Gateway MQTT Connected", broker=settings.MQTT_HOST)
        # Subscribe to all telemetry and acks in this society
        topic = f"jaljasoos/{settings.SOCIETY_ID}/+/+/+/telemetry"
        client.subscribe(topic, qos=0)
        client.subscribe(f"jaljasoos/{settings.SOCIETY_ID}/+/+/+/ack", qos=2)
    else:
        logger.error("Edge Gateway MQTT Connect Failed", reason_code=reason_code)

def on_message(client, userdata, msg):
    topic_info = parse_topic(msg.topic)
    if not topic_info:
        return

    msg_type = topic_info["message_type"]
    if msg_type == "telemetry":
        handle_telemetry(client, topic_info, msg.payload)
    elif msg_type == "ack":
        handle_ack(topic_info, msg.payload)

def handle_telemetry(client: mqtt.Client, topic_info: dict, payload: bytes):
    is_valid, data, err = validate_telemetry(payload)
    if not is_valid:
        logger.warning("Invalid telemetry payload", error=err)
        return

    # Skip actual processing if we have duplicate timestamp check (optional on edge for speed)
    node_id = data["node_id"]
    flow = data.get("flow_lpm")
    pressure = data.get("pressure_bar")
    acoustic = data.get("acoustic_rms")

    # Run local AI Inference
    is_anomaly, confidence = ai_engine.evaluate_telemetry(flow, pressure, acoustic)

    with SessionLocal() as db:
        # Save raw telemetry to Edge DB
        tel = EdgeTelemetry(
            node_id=node_id,
            timestamp=datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00")),
            flow_lpm=flow,
            pressure_bar=pressure,
            acoustic_rms=acoustic,
            pump_state=data.get("pump_state"),
            is_anomaly=is_anomaly,
            synced_to_cloud=False
        )
        db.add(tel)

        # Local Offline-First Valve Control
        if is_anomaly:
            # 1. Create incident locally
            inc_ref = f"INC-EDGE-{uuid.uuid4().hex[:6].upper()}"
            incident = EdgeIncident(
                incident_ref=inc_ref,
                node_id=node_id,
                status="AUTOMATED_ISOLATION",
                severity="HIGH",
                ai_confidence=confidence,
                synced_to_cloud=False
            )
            db.add(incident)
            
            # 2. Trigger Valve immediately via MQTT (QoS 2)
            cmd_id = str(uuid.uuid4())
            cmd_payload = {
                "command_id": cmd_id,
                "action": "CLOSE",
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "issuer": "EDGE_GATEWAY",
                "timeout_ms": 10000
            }
            cmd_topic = f"jaljasoos/{topic_info['society_id']}/{topic_info['building_id']}/{topic_info['zone_id']}/{node_id}/command"
            client.publish(cmd_topic, json.dumps(cmd_payload), qos=2)
            logger.critical("Anomaly Detected: Local Valve ISOLATION Triggered", node_id=node_id, incident=inc_ref)

            # 3. Queue cloud sync
            sync_event = EdgeSyncQueue(
                event_type="INCIDENT_CREATED",
                payload={"incident_ref": inc_ref, "node_id": node_id, "action": "CLOSE_VALVE"}
            )
            db.add(sync_event)

        db.commit()

def handle_ack(topic_info: dict, payload: bytes):
    logger.info("Received Valve ACK", node_id=topic_info["node_id"], payload=payload.decode())

def start_mqtt_worker():
    client = mqtt.Client(client_id="jaljasoos-edge-gateway", protocol=mqtt.MQTTv5)
    if settings.MQTT_USER:
        client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASS)
    
    client.on_connect = on_connect
    client.on_message = on_message
    
    logger.info("Starting MQTT Worker Thread...")
    while True:
        try:
            client.connect(settings.MQTT_HOST, settings.MQTT_PORT, keepalive=60)
            client.loop_start()
            break
        except Exception as e:
            logger.warning("Waiting for Mosquitto...", error=str(e))
            time.sleep(2)
    return client
