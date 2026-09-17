"""Simulator configuration via environment variables."""
import os
from dotenv import load_dotenv

load_dotenv()

MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")

SOCIETY_ID = os.getenv("SIM_SOCIETY_ID", "society01")
BUILDING_ID = os.getenv("SIM_BUILDING_ID", "buildingA")

TELEMETRY_INTERVAL_SEC = float(os.getenv("SIM_TELEMETRY_INTERVAL", "2.0"))
HEALTH_INTERVAL_SEC = float(os.getenv("SIM_HEALTH_INTERVAL", "30.0"))

SCENARIO = os.getenv("SIM_SCENARIO", "normal")  # normal, leak, pump_startup, sensor_failure, node_offline
SCENARIO_DURATION_SEC = int(os.getenv("SIM_SCENARIO_DURATION", "120"))
