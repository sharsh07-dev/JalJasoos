"""
MQTT client wrapper for the JalJasoos simulator.
Connects to a real Mosquitto broker (not a mock).
"""
import time
import paho.mqtt.client as mqtt
import structlog

from simulator.config import MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_USERNAME, MQTT_PASSWORD

logger = structlog.get_logger()


def create_mqtt_client(client_id: str = "jaljasoos-simulator") -> mqtt.Client:
    """Create and connect a real paho-mqtt client."""
    client = mqtt.Client(
        client_id=client_id,
        protocol=mqtt.MQTTv5,
    )

    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            logger.info(
                "MQTT connected",
                broker=MQTT_BROKER_HOST,
                port=MQTT_BROKER_PORT,
                mode="SIMULATION",
            )
        else:
            logger.error("MQTT connection failed", reason_code=reason_code)

    def on_disconnect(client, userdata, flags, reason_code, properties):
        logger.warning("MQTT disconnected", reason_code=reason_code)
        if reason_code != 0:
            logger.info("Attempting MQTT reconnect...")
            # Reconnect handled by loop_start

    def on_publish(client, userdata, mid, reason_code, properties):
        pass  # Suppress verbose publish confirmations

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish

    # Attempt connection with retry
    max_retries = 10
    for attempt in range(1, max_retries + 1):
        try:
            client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, keepalive=60)
            client.loop_start()
            logger.info(
                "MQTT connecting",
                host=MQTT_BROKER_HOST,
                port=MQTT_BROKER_PORT,
                attempt=attempt,
            )
            time.sleep(1.5)  # Give time for on_connect to fire
            return client
        except Exception as e:
            logger.warning("MQTT connect attempt failed", attempt=attempt, error=str(e))
            if attempt < max_retries:
                time.sleep(2 ** min(attempt, 5))  # Exponential backoff
            else:
                raise RuntimeError(
                    f"Could not connect to MQTT broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT} "
                    f"after {max_retries} attempts. Is Mosquitto running?"
                )
    return client  # unreachable but satisfies type checker
