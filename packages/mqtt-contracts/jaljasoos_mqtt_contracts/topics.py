"""
JalJasoos MQTT Topic Definitions

Topic format:
    jaljasoos/{society_id}/{building_id}/{zone_id}/{node_id}/{message_type}

Example:
    jaljasoos/society01/buildingA/zone03/NODE-A3-04/telemetry
"""
from dataclasses import dataclass
from typing import Optional


SOCIETY_PREFIX = "jaljasoos"

# QoS levels
QOS_TELEMETRY = 0      # Best effort — high frequency, loss acceptable
QOS_HEALTH = 1         # At least once — important but not critical
QOS_COMMAND = 2        # Exactly once — valve commands are safety-critical
QOS_ACK = 2            # Exactly once — command acknowledgements
QOS_EVENT = 1          # At least once — events must arrive

# Wildcard topic subscriptions (for broker/gateway)
TELEMETRY_WILDCARD = "jaljasoos/+/+/+/+/telemetry"
HEALTH_WILDCARD = "jaljasoos/+/+/+/+/health"
COMMAND_WILDCARD = "jaljasoos/+/+/+/+/command"
ACK_WILDCARD = "jaljasoos/+/+/+/+/ack"
EVENT_WILDCARD = "jaljasoos/+/+/+/+/event"
VALVE_WILDCARD = "jaljasoos/+/+/+/+/valve"


@dataclass
class TopicAddress:
    society_id: str
    building_id: str
    zone_id: str
    node_id: str

    def _base(self) -> str:
        return f"{SOCIETY_PREFIX}/{self.society_id}/{self.building_id}/{self.zone_id}/{self.node_id}"

    @property
    def telemetry(self) -> str:
        return f"{self._base()}/telemetry"

    @property
    def health(self) -> str:
        return f"{self._base()}/health"

    @property
    def command(self) -> str:
        return f"{self._base()}/command"

    @property
    def ack(self) -> str:
        return f"{self._base()}/ack"

    @property
    def event(self) -> str:
        return f"{self._base()}/event"

    @property
    def valve(self) -> str:
        return f"{self._base()}/valve"


def parse_topic(topic: str) -> Optional[dict]:
    """
    Parse a full MQTT topic string into its components.
    Returns None if the topic doesn't match the JalJasoos format.
    """
    parts = topic.split("/")
    if len(parts) != 6 or parts[0] != SOCIETY_PREFIX:
        return None
    return {
        "society_id": parts[1],
        "building_id": parts[2],
        "zone_id": parts[3],
        "node_id": parts[4],
        "message_type": parts[5],
    }
