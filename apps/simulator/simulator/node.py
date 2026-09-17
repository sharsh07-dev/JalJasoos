"""
Virtual ESP32 Node

Each virtual node:
 - Has a unique node_id
 - Maintains a PipelineState physics engine
 - Publishes telemetry + health over real MQTT
 - Is tagged with MODE=SIMULATION in every payload

NEVER mixes SIMULATION payloads with LIVE_HARDWARE payloads.
"""
import json
import time
import uuid
import random
from datetime import datetime, timezone
from typing import Optional

import paho.mqtt.client as mqtt
import structlog

from simulator.physics.pipeline import PipelineState
from simulator.scenarios.base import BaseScenario
from simulator.scenarios.normal import NormalScenario
from simulator.scenarios.leak import LeakScenario
from simulator.scenarios.pump_startup import PumpStartupScenario
from simulator.scenarios.sensor_failure import SensorFailureScenario
from simulator.scenarios.node_offline import NodeOfflineScenario

logger = structlog.get_logger()


class VirtualNode:
    """Simulates a single ESP32 sensor node."""

    SCENARIOS = {
        "normal": NormalScenario,
        "leak": LeakScenario,
        "pump_startup": PumpStartupScenario,
        "sensor_failure": SensorFailureScenario,
        "node_offline": NodeOfflineScenario,
    }

    def __init__(
        self,
        node_id: str,
        society_id: str,
        building_id: str,
        zone_id: str,
        mqtt_client: mqtt.Client,
        scenario_name: str = "normal",
        scenario_duration_sec: int = 120,
        telemetry_interval: float = 2.0,
        health_interval: float = 30.0,
    ):
        self.node_id = node_id
        self.society_id = society_id
        self.building_id = building_id
        self.zone_id = zone_id
        self.mqtt = mqtt_client
        self.telemetry_interval = telemetry_interval
        self.health_interval = health_interval

        # Topic helpers
        self._base_topic = f"jaljasoos/{society_id}/{building_id}/{zone_id}/{node_id}"

        # Physics engine
        self.pipeline = PipelineState(
            base_flow_lpm=random.uniform(15.0, 22.0),
            base_pressure_bar=random.uniform(2.5, 3.2),
            base_tank_level=random.uniform(60.0, 85.0),
        )

        # Scenario
        scenario_cls = self.SCENARIOS.get(scenario_name, NormalScenario)
        self.scenario: BaseScenario = scenario_cls(self.pipeline, duration_sec=scenario_duration_sec)

        # Battery simulation (slowly depletes)
        self._battery = random.randint(70, 98)
        self._rssi = random.randint(-75, -45)

        self._last_telemetry = 0.0
        self._last_health = 0.0

        logger.info(
            "VirtualNode initialized",
            node_id=node_id,
            scenario=self.scenario.name,
            mode="SIMULATION",
        )

    def _topic(self, suffix: str) -> str:
        return f"{self._base_topic}/{suffix}"

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def build_telemetry_payload(self) -> dict:
        t = time.time()
        return {
            # WARNING: SIMULATION MODE — not real hardware
            "_mode": "SIMULATION",
            "node_id": self.node_id,
            "timestamp": self._now_iso(),
            "flow_lpm": self.pipeline.get_flow_lpm(t),
            "pressure_bar": self.pipeline.get_pressure_bar(t),
            "acoustic_rms": self.pipeline.get_acoustic_rms(t),
            "pump_state": self.pipeline.pump_on,
            "tank_level_percent": self.pipeline.get_tank_level_percent(t),
            "motor_current_a": self.pipeline.get_motor_current_a(t),
            "battery_percent": self._battery,
            "signal_rssi": self._rssi,
        }

    def build_health_payload(self) -> dict:
        return {
            "_mode": "SIMULATION",
            "node_id": self.node_id,
            "timestamp": self._now_iso(),
            "status": "ONLINE",
            "uptime_seconds": self.pipeline.uptime_seconds(),
            "free_heap_bytes": random.randint(120000, 180000),
            "wifi_rssi": self._rssi,
            "mqtt_reconnects": 0,
            "battery_percent": self._battery,
            "cpu_temp_c": round(random.uniform(42.0, 58.0), 1),
            "firmware_version": "sim-0.1.0",
        }

    def _publish(self, topic: str, payload: dict, qos: int = 0) -> bool:
        try:
            result = self.mqtt.publish(
                topic,
                json.dumps(payload),
                qos=qos,
                retain=False,
            )
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            logger.error("Publish failed", topic=topic, error=str(e))
            return False

    def tick(self):
        """Called in the main loop. Publishes data on schedule."""
        now = time.time()

        # Drive scenario
        self.scenario.tick()

        # Check if node_offline scenario has suppressed publishing
        should_publish = True
        if hasattr(self.scenario, "should_publish"):
            should_publish = self.scenario.should_publish()

        if should_publish:
            # Publish telemetry
            if now - self._last_telemetry >= self.telemetry_interval:
                payload = self.build_telemetry_payload()
                success = self._publish(
                    self._topic("telemetry"),
                    payload,
                    qos=0,  # QoS 0 for high-frequency telemetry
                )
                if success:
                    logger.debug(
                        "Telemetry published",
                        node_id=self.node_id,
                        flow=payload.get("flow_lpm"),
                        pressure=payload.get("pressure_bar"),
                        scenario=self.scenario.name,
                    )
                self._last_telemetry = now

            # Publish health
            if now - self._last_health >= self.health_interval:
                health = self.build_health_payload()
                self._publish(self._topic("health"), health, qos=1)
                self._last_health = now

                # Slowly drain battery
                if self._battery > 5:
                    self._battery -= 1

        # Publish NODE_BOOT event on first tick
        if self._last_health == 0 or self._last_health == now:
            event = {
                "_mode": "SIMULATION",
                "event_id": str(uuid.uuid4()),
                "node_id": self.node_id,
                "event_type": "NODE_BOOT",
                "timestamp": self._now_iso(),
                "severity": "INFO",
                "message": f"Node {self.node_id} simulator started (scenario: {self.scenario.name})",
            }
            self._publish(self._topic("event"), event, qos=1)
