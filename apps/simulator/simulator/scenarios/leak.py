"""Leak scenario — the most important scenario in JalJasoos."""
import time
from simulator.scenarios.base import BaseScenario


class LeakScenario(BaseScenario):
    name = "LEAK"
    description = "Simulates a pipeline leak with acoustic, pressure and flow signatures"

    def __init__(self, pipeline, duration_sec=120, magnitude=0.7, start_at_sec=15):
        super().__init__(pipeline, duration_sec)
        self.magnitude = magnitude
        self.start_at_sec = start_at_sec
        self._leak_triggered = False
        self._leak_trigger_time = None

    def tick(self):
        elapsed = self.elapsed()

        # Trigger leak after start_at_sec
        if elapsed >= self.start_at_sec and not self._leak_triggered:
            self.pipeline.trigger_leak(magnitude=self.magnitude)
            self._leak_triggered = True
            self._leak_trigger_time = time.time()

        # The physics engine generates the leak signatures automatically.
        # This scenario just toggles the leak flag and magnitude.
        # A real repair would call pipeline.stop_leak().
