"""
JalJasoos MQTT Payload Validator

Validates incoming MQTT payloads against JSON schemas.
Rejects malformed, missing-field, or out-of-range messages.
"""
import json
import os
from typing import Tuple, Optional
from datetime import datetime, timezone, timedelta

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

_SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "schemas")
_SCHEMAS: dict = {}


def _load_schema(name: str) -> dict:
    if name not in _SCHEMAS:
        path = os.path.join(_SCHEMA_DIR, f"{name}.json")
        with open(path) as f:
            _SCHEMAS[name] = json.load(f)
    return _SCHEMAS[name]


def validate_payload(message_type: str, raw_payload: bytes) -> Tuple[bool, Optional[dict], Optional[str]]:
    """
    Validate a raw MQTT payload.

    Returns:
        (is_valid, parsed_payload, error_message)
    """
    # 1. JSON parse
    try:
        payload = json.loads(raw_payload.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return False, None, f"JSON decode error: {e}"

    # 2. Schema validation
    if HAS_JSONSCHEMA:
        try:
            schema = _load_schema(message_type)
            jsonschema.validate(instance=payload, schema=schema)
        except jsonschema.ValidationError as e:
            return False, None, f"Schema validation failed: {e.message}"
        except FileNotFoundError:
            pass  # No schema file for this type — allow

    # 3. Timestamp sanity check (clock drift detection)
    if "timestamp" in payload:
        try:
            device_ts = datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            drift = abs((now - device_ts).total_seconds())
            if drift > 300:  # > 5 minutes drift
                payload["_clock_drift_seconds"] = drift
                payload["_clock_drift_warning"] = True
        except (ValueError, KeyError):
            return False, None, "Invalid timestamp format"

    return True, payload, None


def validate_telemetry(raw_payload: bytes) -> Tuple[bool, Optional[dict], Optional[str]]:
    return validate_payload("telemetry", raw_payload)


def validate_health(raw_payload: bytes) -> Tuple[bool, Optional[dict], Optional[str]]:
    return validate_payload("health", raw_payload)


def validate_command(raw_payload: bytes) -> Tuple[bool, Optional[dict], Optional[str]]:
    return validate_payload("command", raw_payload)


def validate_ack(raw_payload: bytes) -> Tuple[bool, Optional[dict], Optional[str]]:
    return validate_payload("ack", raw_payload)
