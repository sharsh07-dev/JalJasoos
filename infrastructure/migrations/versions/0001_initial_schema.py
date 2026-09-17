"""Initial schema: create all JalJasoos tables

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-09-17

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── ENUMS ────────────────────────────────────────────────────────────────
    op.execute("CREATE TYPE userrole AS ENUM ('SUPER_ADMIN','FACILITY_MANAGER','MAINTENANCE_STAFF','RESIDENT')")
    op.execute("CREATE TYPE nodestatus AS ENUM ('ONLINE','OFFLINE','DEGRADED','MAINTENANCE','DECOMMISSIONED')")
    op.execute("CREATE TYPE valvestatus AS ENUM ('OPEN','CLOSING','CLOSED','OPENING','FAULT','UNKNOWN')")
    op.execute("CREATE TYPE sensortype AS ENUM ('FLOW','PRESSURE','ACOUSTIC','TANK_LEVEL','MOTOR_CURRENT','PUMP_STATE')")
    op.execute("CREATE TYPE pumpstatus AS ENUM ('ON','OFF','FAULT','UNKNOWN')")
    op.execute("CREATE TYPE incidentstatus AS ENUM ('NORMAL','ANOMALY_DETECTED','MULTI_SENSOR_VERIFICATION','LEAK_SUSPECTED','LEAK_CONFIRMED','ZONE_LOCALIZED','AUTOMATED_ISOLATION','MAINTENANCE_ASSIGNED','REPAIR_COMPLETED','POST_REPAIR_VERIFICATION','RESOLVED','FALSE_ALARM')")
    op.execute("CREATE TYPE incidentseverity AS ENUM ('LOW','MEDIUM','HIGH','CRITICAL')")
    op.execute("CREATE TYPE valveaction AS ENUM ('OPEN','CLOSE','STOP','PARTIAL')")
    op.execute("CREATE TYPE commandstatus AS ENUM ('PENDING','SENT','RECEIVED','ACTUATION_STARTED','COMPLETED','FAILED','TIMEOUT')")
    op.execute("CREATE TYPE maintenancestatus AS ENUM ('OPEN','ASSIGNED','IN_PROGRESS','REPAIR_COMPLETED','VERIFIED','CLOSED')")
    op.execute("CREATE TYPE maintenancepriority AS ENUM ('LOW','MEDIUM','HIGH','CRITICAL')")
    op.execute("CREATE TYPE alertseverity AS ENUM ('INFO','WARNING','CRITICAL')")
    op.execute("CREATE TYPE modeltype AS ENUM ('PINN','FUSION','THRESHOLD')")
    op.execute("CREATE TYPE syncstatus AS ENUM ('PENDING','SYNCING','SYNCED','FAILED','DEAD_LETTER')")

    # ── ROLES ─────────────────────────────────────────────────────────────────
    op.create_table(
        "roles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.Enum("SUPER_ADMIN","FACILITY_MANAGER","MAINTENANCE_STAFF","RESIDENT", name="userrole"), nullable=False, unique=True),
        sa.Column("description", sa.String, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── SOCIETIES ──────────────────────────────────────────────────────────────
    op.create_table(
        "societies",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("address", sa.String, nullable=True),
        sa.Column("city", sa.String, nullable=True),
        sa.Column("state", sa.String, nullable=True),
        sa.Column("pincode", sa.String, nullable=True),
        sa.Column("contact_email", sa.String, nullable=True),
        sa.Column("contact_phone", sa.String, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── USERS ──────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String, nullable=False, unique=True),
        sa.Column("full_name", sa.String, nullable=False),
        sa.Column("hashed_password", sa.String, nullable=False),
        sa.Column("role_id", UUID(as_uuid=True), sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("society_id", UUID(as_uuid=True), sa.ForeignKey("societies.id"), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, default=True),
        sa.Column("is_verified", sa.Boolean, nullable=False, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"])

    # ── PERMISSIONS ────────────────────────────────────────────────────────────
    op.create_table(
        "permissions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("role_name", sa.Enum("SUPER_ADMIN","FACILITY_MANAGER","MAINTENANCE_STAFF","RESIDENT", name="userrole"), nullable=False),
        sa.Column("resource", sa.String, nullable=False),
        sa.Column("action", sa.String, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── BUILDINGS ──────────────────────────────────────────────────────────────
    op.create_table(
        "buildings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("code", sa.String, nullable=False),
        sa.Column("society_id", UUID(as_uuid=True), sa.ForeignKey("societies.id"), nullable=False),
        sa.Column("total_floors", sa.Integer, nullable=False, default=1),
        sa.Column("latitude", sa.Float, nullable=True),
        sa.Column("longitude", sa.Float, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_buildings_society_id", "buildings", ["society_id"])

    # ── FLOORS ────────────────────────────────────────────────────────────────
    op.create_table(
        "floors",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("number", sa.Integer, nullable=False),
        sa.Column("label", sa.String, nullable=True),
        sa.Column("building_id", UUID(as_uuid=True), sa.ForeignKey("buildings.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_floors_building_id", "floors", ["building_id"])

    # ── ZONES ─────────────────────────────────────────────────────────────────
    op.create_table(
        "zones",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("code", sa.String, nullable=False),
        sa.Column("floor_id", UUID(as_uuid=True), sa.ForeignKey("floors.id"), nullable=False),
        sa.Column("description", sa.String, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_zones_floor_id", "zones", ["floor_id"])

    # ── NODES ─────────────────────────────────────────────────────────────────
    op.create_table(
        "nodes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("node_id", sa.String, nullable=False, unique=True),
        sa.Column("serial_number", sa.String, nullable=True, unique=True),
        sa.Column("zone_id", UUID(as_uuid=True), sa.ForeignKey("zones.id"), nullable=False),
        sa.Column("firmware_version", sa.String, nullable=True),
        sa.Column("hardware_version", sa.String, nullable=True),
        sa.Column("last_seen", sa.DateTime(timezone=True), nullable=True),
        sa.Column("battery_percent", sa.Integer, nullable=True),
        sa.Column("rssi_dbm", sa.Integer, nullable=True),
        sa.Column("status", sa.Enum("ONLINE","OFFLINE","DEGRADED","MAINTENANCE","DECOMMISSIONED", name="nodestatus"), nullable=False, default="OFFLINE"),
        sa.Column("installation_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_nodes_node_id", "nodes", ["node_id"])
    op.create_index("ix_nodes_zone_id", "nodes", ["zone_id"])

    # ── SENSORS ───────────────────────────────────────────────────────────────
    op.create_table(
        "sensors",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("node_id", UUID(as_uuid=True), sa.ForeignKey("nodes.id"), nullable=False),
        sa.Column("sensor_type", sa.Enum("FLOW","PRESSURE","ACOUSTIC","TANK_LEVEL","MOTOR_CURRENT","PUMP_STATE", name="sensortype"), nullable=False),
        sa.Column("unit", sa.String, nullable=True),
        sa.Column("calibration_offset", sa.Float, default=0.0),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── VALVES ────────────────────────────────────────────────────────────────
    op.create_table(
        "valves",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("node_id", UUID(as_uuid=True), sa.ForeignKey("nodes.id"), nullable=False),
        sa.Column("label", sa.String, nullable=False),
        sa.Column("status", sa.Enum("OPEN","CLOSING","CLOSED","OPENING","FAULT","UNKNOWN", name="valvestatus"), nullable=False, default="UNKNOWN"),
        sa.Column("last_command_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_valves_node_id", "valves", ["node_id"])

    # ── PUMPS ─────────────────────────────────────────────────────────────────
    op.create_table(
        "pumps",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("label", sa.String, nullable=False),
        sa.Column("zone_id", UUID(as_uuid=True), sa.ForeignKey("zones.id"), nullable=True),
        sa.Column("status", sa.Enum("ON","OFF","FAULT","UNKNOWN", name="pumpstatus"), default="UNKNOWN"),
        sa.Column("rated_current_a", sa.Float, nullable=True),
        sa.Column("rated_flow_lpm", sa.Float, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── TANKS ─────────────────────────────────────────────────────────────────
    op.create_table(
        "tanks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("label", sa.String, nullable=False),
        sa.Column("zone_id", UUID(as_uuid=True), sa.ForeignKey("zones.id"), nullable=True),
        sa.Column("capacity_liters", sa.Float, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── TELEMETRY ─────────────────────────────────────────────────────────────
    op.create_table(
        "telemetry",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("node_id", UUID(as_uuid=True), sa.ForeignKey("nodes.id"), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ingested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("flow_lpm", sa.Float, nullable=True),
        sa.Column("pressure_bar", sa.Float, nullable=True),
        sa.Column("acoustic_rms", sa.Float, nullable=True),
        sa.Column("pump_state", sa.Boolean, nullable=True),
        sa.Column("tank_level_percent", sa.Float, nullable=True),
        sa.Column("motor_current_a", sa.Float, nullable=True),
        sa.Column("battery_percent", sa.Integer, nullable=True),
        sa.Column("signal_rssi", sa.Integer, nullable=True),
        sa.Column("is_anomaly", sa.Boolean, nullable=False, default=False),
        sa.Column("source", sa.String, nullable=False, default="DEVICE"),
    )
    op.create_index("ix_telemetry_node_id", "telemetry", ["node_id"])
    op.create_index("ix_telemetry_timestamp", "telemetry", ["timestamp"])
    op.create_index("ix_telemetry_node_id_timestamp", "telemetry", ["node_id", "timestamp"])

    # ── INCIDENTS ─────────────────────────────────────────────────────────────
    op.create_table(
        "incidents",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("incident_ref", sa.String, nullable=False, unique=True),
        sa.Column("node_id", UUID(as_uuid=True), sa.ForeignKey("nodes.id"), nullable=False),
        sa.Column("status", sa.Enum("NORMAL","ANOMALY_DETECTED","MULTI_SENSOR_VERIFICATION","LEAK_SUSPECTED","LEAK_CONFIRMED","ZONE_LOCALIZED","AUTOMATED_ISOLATION","MAINTENANCE_ASSIGNED","REPAIR_COMPLETED","POST_REPAIR_VERIFICATION","RESOLVED","FALSE_ALARM", name="incidentstatus"), nullable=False),
        sa.Column("severity", sa.Enum("LOW","MEDIUM","HIGH","CRITICAL", name="incidentseverity"), nullable=False),
        sa.Column("detection_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("localization_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("isolation_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolution_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("flow_at_detection", sa.Float, nullable=True),
        sa.Column("pressure_at_detection", sa.Float, nullable=True),
        sa.Column("acoustic_at_detection", sa.Float, nullable=True),
        sa.Column("ai_confidence", sa.Float, nullable=True),
        sa.Column("estimated_loss_liters", sa.Float, nullable=True),
        sa.Column("acknowledged_by_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("notes", sa.String, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_incidents_node_id", "incidents", ["node_id"])
    op.create_index("ix_incidents_incident_ref", "incidents", ["incident_ref"])

    # ── INCIDENT EVENTS ───────────────────────────────────────────────────────
    op.create_table(
        "incident_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("incident_id", UUID(as_uuid=True), sa.ForeignKey("incidents.id"), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("from_status", sa.Enum("NORMAL","ANOMALY_DETECTED","MULTI_SENSOR_VERIFICATION","LEAK_SUSPECTED","LEAK_CONFIRMED","ZONE_LOCALIZED","AUTOMATED_ISOLATION","MAINTENANCE_ASSIGNED","REPAIR_COMPLETED","POST_REPAIR_VERIFICATION","RESOLVED","FALSE_ALARM", name="incidentstatus"), nullable=True),
        sa.Column("to_status", sa.Enum("NORMAL","ANOMALY_DETECTED","MULTI_SENSOR_VERIFICATION","LEAK_SUSPECTED","LEAK_CONFIRMED","ZONE_LOCALIZED","AUTOMATED_ISOLATION","MAINTENANCE_ASSIGNED","REPAIR_COMPLETED","POST_REPAIR_VERIFICATION","RESOLVED","FALSE_ALARM", name="incidentstatus"), nullable=False),
        sa.Column("triggered_by", sa.String, nullable=False),
        sa.Column("actor_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("message", sa.String, nullable=False),
        sa.Column("metadata", JSON, nullable=True),
    )
    op.create_index("ix_incident_events_incident_id", "incident_events", ["incident_id"])

    # ── VALVE COMMANDS ────────────────────────────────────────────────────────
    op.create_table(
        "valve_commands",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("valve_id", UUID(as_uuid=True), sa.ForeignKey("valves.id"), nullable=False),
        sa.Column("incident_id", UUID(as_uuid=True), sa.ForeignKey("incidents.id"), nullable=True),
        sa.Column("action", sa.Enum("OPEN","CLOSE","STOP","PARTIAL", name="valveaction"), nullable=False),
        sa.Column("status", sa.Enum("PENDING","SENT","RECEIVED","ACTUATION_STARTED","COMPLETED","FAILED","TIMEOUT", name="commandstatus"), nullable=False),
        sa.Column("issued_by", sa.String, nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actuation_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("command_latency_ms", sa.Float, nullable=True),
        sa.Column("actuation_time_ms", sa.Float, nullable=True),
        sa.Column("confirmation_time_ms", sa.Float, nullable=True),
        sa.Column("retry_count", sa.Integer, default=0),
        sa.Column("failure_reason", sa.String, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_valve_commands_valve_id", "valve_commands", ["valve_id"])

    # ── MAINTENANCE TASKS ────────────────────────────────────────────────────
    op.create_table(
        "maintenance_tasks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("task_ref", sa.String, nullable=False, unique=True),
        sa.Column("incident_id", UUID(as_uuid=True), sa.ForeignKey("incidents.id"), nullable=False),
        sa.Column("assigned_to_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("status", sa.Enum("OPEN","ASSIGNED","IN_PROGRESS","REPAIR_COMPLETED","VERIFIED","CLOSED", name="maintenancestatus"), nullable=False),
        sa.Column("priority", sa.Enum("LOW","MEDIUM","HIGH","CRITICAL", name="maintenancepriority"), nullable=False),
        sa.Column("title", sa.String, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verified_by_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_maintenance_tasks_incident_id", "maintenance_tasks", ["incident_id"])

    # ── MAINTENANCE LOGS ──────────────────────────────────────────────────────
    op.create_table(
        "maintenance_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("task_id", UUID(as_uuid=True), sa.ForeignKey("maintenance_tasks.id"), nullable=False),
        sa.Column("logged_by_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("note", sa.Text, nullable=True),
        sa.Column("attachments", JSON, nullable=True),
        sa.Column("action_taken", sa.String, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── ALERTS ────────────────────────────────────────────────────────────────
    op.create_table(
        "alerts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("incident_id", UUID(as_uuid=True), sa.ForeignKey("incidents.id"), nullable=True),
        sa.Column("node_id", UUID(as_uuid=True), sa.ForeignKey("nodes.id"), nullable=True),
        sa.Column("severity", sa.Enum("INFO","WARNING","CRITICAL", name="alertseverity"), nullable=False),
        sa.Column("title", sa.String, nullable=False),
        sa.Column("message", sa.String, nullable=False),
        sa.Column("metadata", JSON, nullable=True),
        sa.Column("is_acknowledged", sa.Boolean, default=False),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("acknowledged_by_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── NOTIFICATIONS ─────────────────────────────────────────────────────────
    op.create_table(
        "notifications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("alert_id", UUID(as_uuid=True), sa.ForeignKey("alerts.id"), nullable=True),
        sa.Column("title", sa.String, nullable=False),
        sa.Column("body", sa.String, nullable=False),
        sa.Column("is_read", sa.Boolean, default=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("channel", sa.String, default="IN_APP"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])

    # ── DEVICE HEALTH ─────────────────────────────────────────────────────────
    op.create_table(
        "device_health",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("node_id", UUID(as_uuid=True), sa.ForeignKey("nodes.id"), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("uptime_seconds", sa.Integer, nullable=True),
        sa.Column("free_heap_bytes", sa.Integer, nullable=True),
        sa.Column("wifi_rssi", sa.Integer, nullable=True),
        sa.Column("mqtt_reconnects", sa.Integer, nullable=True),
        sa.Column("battery_percent", sa.Integer, nullable=True),
        sa.Column("cpu_temp_c", sa.Float, nullable=True),
    )
    op.create_index("ix_device_health_node_id", "device_health", ["node_id"])
    op.create_index("ix_device_health_timestamp", "device_health", ["timestamp"])

    # ── MODEL VERSIONS ────────────────────────────────────────────────────────
    op.create_table(
        "model_versions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("model_type", sa.Enum("PINN","FUSION","THRESHOLD", name="modeltype"), nullable=False),
        sa.Column("version", sa.String, nullable=False),
        sa.Column("file_path", sa.String, nullable=True),
        sa.Column("is_active", sa.Boolean, default=False),
        sa.Column("training_notes", sa.String, nullable=True),
        sa.Column("metrics", JSON, nullable=True),
        sa.Column("deployed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deployed_by_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── MODEL PREDICTIONS ─────────────────────────────────────────────────────
    op.create_table(
        "model_predictions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("incident_id", UUID(as_uuid=True), sa.ForeignKey("incidents.id"), nullable=False),
        sa.Column("model_version_id", UUID(as_uuid=True), sa.ForeignKey("model_versions.id"), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_score", sa.Float, nullable=True),
        sa.Column("confidence", sa.Float, nullable=True),
        sa.Column("prediction_label", sa.String, nullable=True),
        sa.Column("features_used", JSON, nullable=True),
        sa.Column("inference_time_ms", sa.Float, nullable=True),
    )
    op.create_index("ix_model_predictions_incident_id", "model_predictions", ["incident_id"])

    # ── AUDIT LOGS ────────────────────────────────────────────────────────────
    op.create_table(
        "audit_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("action", sa.String, nullable=False),
        sa.Column("resource_type", sa.String, nullable=True),
        sa.Column("resource_id", sa.String, nullable=True),
        sa.Column("ip_address", sa.String, nullable=True),
        sa.Column("user_agent", sa.String, nullable=True),
        sa.Column("result", sa.String, nullable=False, default="SUCCESS"),
        sa.Column("metadata", JSON, nullable=True),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_timestamp", "audit_logs", ["timestamp"])

    # ── SYSTEM SETTINGS ───────────────────────────────────────────────────────
    op.create_table(
        "system_settings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("key", sa.String, nullable=False, unique=True),
        sa.Column("value", JSON, nullable=True),
        sa.Column("description", sa.String, nullable=True),
        sa.Column("is_sensitive", sa.Boolean, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # ── EDGE SYNC QUEUE ───────────────────────────────────────────────────────
    op.create_table(
        "edge_sync_queue",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("event_type", sa.String, nullable=False),
        sa.Column("payload", JSON, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("retry_count", sa.Integer, nullable=False, default=0),
        sa.Column("last_attempt", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sync_status", sa.Enum("PENDING","SYNCING","SYNCED","FAILED","DEAD_LETTER", name="syncstatus"), nullable=False, default="PENDING"),
        sa.Column("error_message", sa.String, nullable=True),
    )
    op.create_index("ix_edge_sync_queue_event_type", "edge_sync_queue", ["event_type"])
    op.create_index("ix_edge_sync_queue_sync_status", "edge_sync_queue", ["sync_status"])


def downgrade() -> None:
    op.drop_table("edge_sync_queue")
    op.drop_table("system_settings")
    op.drop_table("audit_logs")
    op.drop_table("model_predictions")
    op.drop_table("model_versions")
    op.drop_table("device_health")
    op.drop_table("notifications")
    op.drop_table("alerts")
    op.drop_table("maintenance_logs")
    op.drop_table("maintenance_tasks")
    op.drop_table("valve_commands")
    op.drop_table("incident_events")
    op.drop_table("incidents")
    op.drop_table("telemetry")
    op.drop_table("tanks")
    op.drop_table("pumps")
    op.drop_table("valves")
    op.drop_table("sensors")
    op.drop_table("nodes")
    op.drop_table("zones")
    op.drop_table("floors")
    op.drop_table("buildings")
    op.drop_table("permissions")
    op.drop_table("users")
    op.drop_table("societies")
    op.drop_table("roles")
    # Drop enums
    for enum in ["syncstatus","modeltype","alertseverity","maintenancepriority","maintenancestatus",
                 "commandstatus","valveaction","incidentseverity","incidentstatus",
                 "pumpstatus","sensortype","valvestatus","nodestatus","userrole"]:
        op.execute(f"DROP TYPE IF EXISTS {enum}")
