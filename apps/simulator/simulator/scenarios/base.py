"""Base scenario class — defines the interface all scenarios must implement."""
import time
from abc import ABC, abstractmethod
from simulator.physics.pipeline import PipelineState


class BaseScenario(ABC):
    """
    A scenario drives the PipelineState over time to produce
    realistic patterns of sensor readings.
    """
    name: str = "BASE"
    description: str = ""

    def __init__(self, pipeline: PipelineState, duration_sec: int = 120):
        self.pipeline = pipeline
        self.duration_sec = duration_sec
        self.start_time = time.time()
        self._step = 0

    def elapsed(self) -> float:
        return time.time() - self.start_time

    def is_complete(self) -> bool:
        return self.elapsed() >= self.duration_sec

    @abstractmethod
    def tick(self):
        """Called once per telemetry interval. Update pipeline state."""
        ...

    def __str__(self):
        return f"{self.name}: {self.description}"
