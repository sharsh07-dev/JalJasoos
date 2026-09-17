"""
JalJasoos Simulator — Main Entry Point

Spins up one or more virtual ESP32 nodes and publishes realistic
MQTT telemetry to a live Mosquitto broker.

WARNING: SIMULATION MODE
All data from this simulator is tagged with _mode=SIMULATION.
Never mix this data with real hardware telemetry.
"""
import time
import click
import structlog
from typing import List

from simulator import MODE_LABEL, SIMULATOR_VERSION
from simulator.config import (
    SOCIETY_ID, BUILDING_ID, TELEMETRY_INTERVAL_SEC,
    HEALTH_INTERVAL_SEC, SCENARIO, SCENARIO_DURATION_SEC,
)
from simulator.mqtt_client import create_mqtt_client
from simulator.node import VirtualNode

logger = structlog.get_logger()

# Pre-defined virtual node topology
DEFAULT_NODES = [
    {"node_id": "NODE-A1-01", "zone_id": "zone01"},
    {"node_id": "NODE-A2-02", "zone_id": "zone02"},
    {"node_id": "NODE-A3-04", "zone_id": "zone03"},
    {"node_id": "NODE-B1-01", "zone_id": "zone04"},
]


@click.command()
@click.option("--scenario", default=SCENARIO, help="Scenario to run: normal, leak, pump_startup, sensor_failure, node_offline")
@click.option("--node-count", default=len(DEFAULT_NODES), type=int, help="Number of virtual nodes")
@click.option("--duration", default=SCENARIO_DURATION_SEC, type=int, help="Scenario duration in seconds")
@click.option("--interval", default=TELEMETRY_INTERVAL_SEC, type=float, help="Telemetry publish interval in seconds")
@click.option("--leak-node", default="NODE-A3-04", help="Node ID to inject leak scenario into (when scenario=leak)")
def run(
    scenario: str,
    node_count: int,
    duration: int,
    interval: float,
    leak_node: str,
):
    """
    JalJasoos ESP32 Simulator.

    Publishes realistic MQTT telemetry to a local Mosquitto broker.
    All data is tagged SIMULATION MODE and must not be mixed with real hardware.
    """
    click.echo(f"")
    click.echo(f"  jj  jjjjj   aaa  lll         jjjj    aaa   sss   ooo   ooo  sss ")
    click.echo(f"  jj    j    a   a  lll        j   j   a   a s     o   o o   o s   ")
    click.echo(f"  jj    j    aaaaa  lll        j   j   aaaaa  sss  o   o o   o  sss")
    click.echo(f"  jj    j    a   a  lll    jj  j   j   a   a     s o   o o   o     s")
    click.echo(f"  jjjjjjj    a   a  lllll   jjj    jjj a   a ssss   ooo   ooo  ssss ")
    click.echo(f"")
    click.echo(f"  *** MODE: {MODE_LABEL} ***")
    click.echo(f"  Version: {SIMULATOR_VERSION}")
    click.echo(f"  Scenario: {scenario.upper()}")
    click.echo(f"  Nodes: {node_count}")
    click.echo(f"  Duration: {duration}s")
    click.echo(f"  Interval: {interval}s")
    click.echo(f"")

    logger.info(
        "JalJasoos Simulator starting",
        mode=MODE_LABEL,
        scenario=scenario,
        node_count=node_count,
        duration=duration,
    )

    # Connect to real MQTT broker
    mqtt_client = create_mqtt_client(client_id=f"jaljasoos-sim-{scenario}")

    # Create virtual nodes
    nodes: List[VirtualNode] = []
    for i, node_def in enumerate(DEFAULT_NODES[:node_count]):
        nid = node_def["node_id"]
        # Only the designated leak_node runs the leak scenario
        node_scenario = scenario if (scenario != "leak" or nid == leak_node) else "normal"

        node = VirtualNode(
            node_id=nid,
            society_id=SOCIETY_ID,
            building_id=BUILDING_ID,
            zone_id=node_def["zone_id"],
            mqtt_client=mqtt_client,
            scenario_name=node_scenario,
            scenario_duration_sec=duration,
            telemetry_interval=interval,
            health_interval=HEALTH_INTERVAL_SEC,
        )
        nodes.append(node)

    click.echo(f"  Nodes online:")
    for node in nodes:
        click.echo(f"    {node.node_id} -> {node.scenario.name}")
    click.echo(f"")
    
    # Listen for dynamic leak injection
    def on_message(client, userdata, msg):
        try:
            import json
            payload = json.loads(msg.payload.decode())
            target_node = payload.get("node_id")
            new_scenario = payload.get("scenario")
            for n in nodes:
                if n.node_id == target_node:
                    n.scenario_name = new_scenario
                    from simulator.scenarios import get_scenario
                    n.scenario = get_scenario(new_scenario)
                    logger.warning(f"Dynamically injected {new_scenario} into {target_node}")
        except Exception:
            pass
            
    mqtt_client.on_message = on_message
    mqtt_client.subscribe("jaljasoos/command/simulator/set_scenario")
    
    click.echo(f"  Publishing to MQTT... Press Ctrl+C to stop.")
    click.echo(f"")

    start = time.time()
    try:
        while True:
            for node in nodes:
                node.tick()

            elapsed = time.time() - start
            if duration > 0 and elapsed >= duration:
                click.echo(f"\n  Scenario complete after {duration}s.")
                break

            time.sleep(interval)
    except KeyboardInterrupt:
        click.echo("\n  Simulator stopped.")
    finally:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        logger.info("Simulator shutdown", mode=MODE_LABEL)


if __name__ == "__main__":
    run()
