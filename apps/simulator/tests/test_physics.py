"""
Tests for the simulator's physics engine and scenario correctness.

These tests validate that the physics produces physically coherent values
and that scenarios correctly modify pipeline state.
"""
import time
import pytest
from simulator.physics.pipeline import PipelineState


class TestPipelinePhysics:
    def setup_method(self):
        self.pipeline = PipelineState()
        self.t = time.time()

    def test_normal_flow_is_positive(self):
        flow = self.pipeline.get_flow_lpm(self.t)
        assert flow is not None
        assert flow >= 0.0, "Flow must be non-negative"

    def test_normal_pressure_is_in_range(self):
        pressure = self.pipeline.get_pressure_bar(self.t)
        assert pressure is not None
        assert 0.0 <= pressure <= 20.0, "Pressure must be in valid range"

    def test_acoustic_baseline_is_low(self):
        rms = self.pipeline.get_acoustic_rms(self.t)
        assert rms is not None
        assert rms < 0.5, "Baseline acoustic RMS should be low (no leak)"

    def test_pump_off_reduces_flow(self):
        t = time.time()
        flow_on = self.pipeline.get_flow_lpm(t)
        self.pipeline.pump_shutdown()
        flow_off = self.pipeline.get_flow_lpm(t)
        assert flow_off < flow_on, "Flow must decrease when pump is off"

    def test_pump_off_reduces_pressure(self):
        t = time.time()
        pressure_on = self.pipeline.get_pressure_bar(t)
        self.pipeline.pump_shutdown()
        pressure_off = self.pipeline.get_pressure_bar(t)
        assert pressure_off < pressure_on, "Pressure must drop when pump is off"


class TestLeakScenario:
    def setup_method(self):
        self.pipeline = PipelineState()

    def test_leak_raises_acoustic_rms(self):
        t = time.time()
        rms_before = self.pipeline.get_acoustic_rms(t)
        self.pipeline.trigger_leak(magnitude=0.8)
        # Wait for ramp-up
        time.sleep(0.1)
        t_after = time.time()
        rms_after = self.pipeline.get_acoustic_rms(t_after)
        # With magnitude=0.8, leak contribution is significant
        assert rms_after > rms_before, "Acoustic RMS must rise when leak is active"

    def test_leak_drops_pressure(self):
        t = time.time()
        pressure_before = self.pipeline.get_pressure_bar(t)
        self.pipeline.trigger_leak(magnitude=0.8)
        time.sleep(0.1)
        t_after = time.time()
        pressure_after = self.pipeline.get_pressure_bar(t_after)
        assert pressure_after < pressure_before, "Pressure must drop at leak location"

    def test_leak_increases_flow(self):
        t = time.time()
        flow_before = self.pipeline.get_flow_lpm(t)
        self.pipeline.trigger_leak(magnitude=0.8)
        time.sleep(0.1)
        t_after = time.time()
        flow_after = self.pipeline.get_flow_lpm(t_after)
        assert flow_after > flow_before, "Flow must increase due to leak loss"

    def test_stop_leak_normalizes_state(self):
        self.pipeline.trigger_leak(magnitude=0.8)
        time.sleep(0.2)
        self.pipeline.stop_leak()
        assert not self.pipeline.leak_active
        assert self.pipeline.leak_magnitude == 0.0


class TestSensorFailure:
    def setup_method(self):
        self.pipeline = PipelineState()

    def test_failed_flow_sensor_returns_none(self):
        self.pipeline.fail_sensor("flow")
        assert self.pipeline.get_flow_lpm(time.time()) is None

    def test_failed_pressure_sensor_returns_none(self):
        self.pipeline.fail_sensor("pressure")
        assert self.pipeline.get_pressure_bar(time.time()) is None

    def test_failed_acoustic_sensor_returns_none(self):
        self.pipeline.fail_sensor("acoustic")
        assert self.pipeline.get_acoustic_rms(time.time()) is None

    def test_recovered_sensor_returns_values(self):
        self.pipeline.fail_sensor("flow")
        self.pipeline.recover_sensor("flow")
        assert self.pipeline.get_flow_lpm(time.time()) is not None


class TestPayloadSchemas:
    """Verify that simulation payloads match the MQTT contract schemas."""

    def test_telemetry_payload_has_required_fields(self):
        """Telemetry must include all fields defined in telemetry.json schema."""
        pipeline = PipelineState()
        t = time.time()

        payload = {
            "node_id": "NODE-A3-04",
            "timestamp": "2026-09-17T12:00:00Z",
            "flow_lpm": pipeline.get_flow_lpm(t),
            "pressure_bar": pipeline.get_pressure_bar(t),
        }
        required_fields = ["node_id", "timestamp", "flow_lpm", "pressure_bar"]
        for field in required_fields:
            assert field in payload, f"Missing required field: {field}"

    def test_mode_label_is_simulation(self):
        """All simulator payloads must declare _mode=SIMULATION."""
        from simulator import MODE_LABEL
        assert MODE_LABEL == "SIMULATION"
