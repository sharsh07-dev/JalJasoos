"""Pump startup scenario — models the transient when the pump kicks on."""
import time
from simulator.scenarios.base import BaseScenario


class PumpStartupScenario(BaseScenario):
    name = "PUMP_STARTUP"
    description = "Pump OFF then ON — models transient pressure/flow surge"

    def __init__(self, pipeline, duration_sec=120):
        super().__init__(pipeline, duration_sec)
        pipeline.pump_shutdown()  # Start with pump off
        self._pump_started = False
        self._startup_time = None

    def tick(self):
        elapsed = self.elapsed()

        if elapsed < 20:
            # Pump off: low flow, low pressure, draining tank
            pass
        elif not self._pump_started:
            # Trigger pump startup at t=20s
            self.pipeline.pump_startup()
            self._pump_started = True
            self._startup_time = time.time()

        if self._pump_started and self._startup_time:
            # Startup transient: pressure spike then normalise
            startup_elapsed = time.time() - self._startup_time
            if startup_elapsed < 3.0:
                # Motor inrush: high current draw during startup
                self.pipeline.base_motor_current_a = 8.5  # Inrush current
                self.pipeline.base_pressure_bar = 3.4     # Pressure surge
            elif startup_elapsed < 8.0:
                # Settling
                self.pipeline.base_motor_current_a = 3.5
                self.pipeline.base_pressure_bar = 2.9
            else:
                # Stable
                self.pipeline.base_motor_current_a = 3.1
                self.pipeline.base_pressure_bar = 2.8
