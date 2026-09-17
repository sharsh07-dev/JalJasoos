"""Normal operation scenario — steady flow with natural variation."""
from simulator.scenarios.base import BaseScenario


class NormalScenario(BaseScenario):
    name = "NORMAL_OPERATION"
    description = "Steady flow with natural household usage variation"

    def tick(self):
        # Normal operation: nothing to change, physics engine handles variation.
        # Occasional usage spikes (tap open event)
        import random
        elapsed = self.elapsed()
        # Simulate morning/evening usage peaks
        if 60 <= elapsed <= 75:
            self.pipeline.base_flow_lpm = 28.0  # Peak usage
        elif 75 < elapsed <= 80:
            self.pipeline.base_flow_lpm = 18.0  # Back to normal
