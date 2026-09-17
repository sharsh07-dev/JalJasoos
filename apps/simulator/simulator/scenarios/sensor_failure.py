"""Sensor failure scenario — a sensor starts returning None/invalid values."""
from simulator.scenarios.base import BaseScenario


class SensorFailureScenario(BaseScenario):
    name = "SENSOR_FAILURE"
    description = "Flow sensor fails at t=10s, then recovers at t=60s"

    def __init__(self, pipeline, duration_sec=120, sensor="flow"):
        super().__init__(pipeline, duration_sec)
        self.sensor = sensor
        self._failed = False
        self._recovered = False

    def tick(self):
        elapsed = self.elapsed()
        if elapsed >= 10 and not self._failed:
            self.pipeline.fail_sensor(self.sensor)
            self._failed = True
        if elapsed >= 60 and self._failed and not self._recovered:
            self.pipeline.recover_sensor(self.sensor)
            self._recovered = True
