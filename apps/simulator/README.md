# JalJasoos Simulator

## ⚠ SIMULATION MODE ⚠

This simulator generates **synthetic** ESP32 telemetry. All payloads are tagged with `_mode: SIMULATION`.
This data must **never** be stored in the same database partition as real hardware data.

## Running Locally

```bash
pip install -e .
# Normal operation
python -m simulator.main --scenario normal --node-count 4
# Inject a leak on NODE-A3-04
python -m simulator.main --scenario leak --leak-node NODE-A3-04 --duration 120
# Pump startup transient
python -m simulator.main --scenario pump_startup
# Sensor failure
python -m simulator.main --scenario sensor_failure
# Node goes offline
python -m simulator.main --scenario node_offline
```

## Available Scenarios

| Scenario | Description |
|---|---|
| `normal` | Steady flow with natural household variation |
| `leak` | Pipeline leak with acoustic, pressure, and flow signatures |
| `pump_startup` | Pump off → transient startup → stable |
| `sensor_failure` | Flow sensor fails then recovers |
| `node_offline` | Node stops publishing (connectivity loss) |

## Physics Engine

All sensor values are generated from the `PipelineState` physics engine in `simulator/physics/pipeline.py`.
Values are not random — they model real pipeline behavior:
- Leak: pressure drop (Bernoulli), excess flow, acoustic turbulence
- Pump startup: motor inrush current, pressure surge
- Sensor failure: returns `null` (not zero)
