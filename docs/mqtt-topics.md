# MQTT Topics & Message Contracts

This document defines the complete MQTT message contract for JalJasoos.

## Topic Format

```
jaljasoos/{society_id}/{building_id}/{zone_id}/{node_id}/{message_type}
```

**Example:**
```
jaljasoos/society01/buildingA/zone03/NODE-A3-04/telemetry
```

## QoS Levels

| Message Type | QoS | Rationale |
|---|---|---|
| `telemetry` | 0 | High-frequency; best-effort acceptable — gaps are tolerable |
| `health` | 1 | At-least-once — node status must arrive |
| `event` | 1 | At-least-once — events must be recorded |
| `command` | 2 | Exactly-once — valve commands are **safety-critical** |
| `ack` | 2 | Exactly-once — command acknowledgements are **safety-critical** |

## Telemetry Payload

**Topic:** `…/telemetry`

```json
{
  "node_id": "NODE-A3-04",
  "timestamp": "2026-09-17T12:30:21Z",
  "flow_lpm": 18.42,
  "pressure_bar": 2.74,
  "acoustic_rms": 0.31,
  "pump_state": true,
  "tank_level_percent": 74.2,
  "motor_current_a": 3.12,
  "battery_percent": 91,
  "signal_rssi": -61
}
```

**Validation rules:**
- `flow_lpm`: `0 ≤ v ≤ 200`
- `pressure_bar`: `0 ≤ v ≤ 20`
- `tank_level_percent`: `0 ≤ v ≤ 100`
- `battery_percent`: `0 ≤ v ≤ 100`
- Clock drift > 5 minutes: payload is annotated `_clock_drift_warning: true` and still ingested with warning log

**Sensor failure:** A sensor failure is indicated by a `null` value, **not zero**.
- `null` = sensor hardware failure
- `0.0` = valid reading of zero (e.g. pump is off, flow is truly zero)

## Health Payload

**Topic:** `…/health`

```json
{
  "node_id": "NODE-A3-04",
  "timestamp": "2026-09-17T12:30:21Z",
  "status": "ONLINE",
  "uptime_seconds": 3600,
  "free_heap_bytes": 152400,
  "wifi_rssi": -61,
  "mqtt_reconnects": 0,
  "battery_percent": 91,
  "cpu_temp_c": 48.2,
  "firmware_version": "1.0.3"
}
```

**Status values:** `ONLINE` | `DEGRADED` | `OFFLINE`

## Command Payload (Gateway → ESP32)

**Topic:** `…/command`
**QoS: 2 (Exactly Once)**

```json
{
  "command_id": "550e8400-e29b-41d4-a716-446655440000",
  "action": "CLOSE",
  "timestamp": "2026-09-17T12:30:21Z",
  "issuer": "EDGE_GATEWAY",
  "timeout_ms": 5000
}
```

**Actions:** `OPEN` | `CLOSE` | `STOP` | `PARTIAL`
**Issuers:** `EDGE_GATEWAY` | `CLOUD_MANUAL` | `SYSTEM`

## ACK Payload (ESP32 → Gateway)

**Topic:** `…/ack`
**QoS: 2 (Exactly Once)**

```json
{
  "command_id": "550e8400-e29b-41d4-a716-446655440000",
  "node_id": "NODE-A3-04",
  "valve_status": "CLOSED",
  "timestamp": "2026-09-17T12:30:22Z",
  "actuation_time_ms": 1240
}
```

**Valve states:** `OPENING` | `OPEN` | `CLOSING` | `CLOSED` | `FAULT` | `UNKNOWN`

> [!IMPORTANT]
> The UI must **never** display "Valve Closed" until it receives this ACK with `valve_status: CLOSED`.
> `COMMAND SENT` and `VALVE CLOSED` are different states.

## Event Payload

**Topic:** `…/event`

```json
{
  "event_id": "uuid",
  "node_id": "NODE-A3-04",
  "event_type": "ACOUSTIC_ANOMALY",
  "timestamp": "2026-09-17T12:30:21Z",
  "severity": "WARNING",
  "message": "Acoustic RMS exceeded 0.4 threshold",
  "metadata": { "rms": 0.47 }
}
```

**Event types:** `NODE_BOOT` | `NODE_SHUTDOWN` | `SENSOR_ERROR` | `VALVE_FAULT` | `MQTT_RECONNECT` | `LOW_BATTERY` | `PRESSURE_SPIKE` | `FLOW_ANOMALY` | `ACOUSTIC_ANOMALY` | `PUMP_FAULT` | `TANK_OVERFLOW` | `TANK_EMPTY`

## Wildcard Subscriptions (Broker/Gateway)

```
jaljasoos/+/+/+/+/telemetry
jaljasoos/+/+/+/+/health
jaljasoos/+/+/+/+/command
jaljasoos/+/+/+/+/ack
jaljasoos/+/+/+/+/event
jaljasoos/+/+/+/+/valve
```

## Simulation vs Hardware

All simulator payloads include `"_mode": "SIMULATION"`.
Real hardware payloads must **never** include this field.
The edge gateway must reject or quarantine any payload where `_mode == SIMULATION` in production mode.
