"""Node offline scenario — the node stops publishing for a period."""
from simulator.scenarios.base import BaseScenario


class NodeOfflineScenario(BaseScenario):
    name = "NODE_OFFLINE"
    description = "Node goes offline at t=10s, reconnects at t=60s"

    def __init__(self, pipeline, duration_sec=120):
        super().__init__(pipeline, duration_sec)
        self.is_offline = False
        self._went_offline = False
        self._came_back = False

    def tick(self):
        elapsed = self.elapsed()
        if elapsed >= 10 and not self._went_offline:
            self.is_offline = True
            self._went_offline = True
        if elapsed >= 60 and self._went_offline and not self._came_back:
            self.is_offline = False
            self._came_back = True

    def should_publish(self) -> bool:
        """Returns False when node is simulating offline state."""
        return not self.is_offline
