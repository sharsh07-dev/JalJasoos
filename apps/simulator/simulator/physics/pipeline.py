"""
Pipeline physics engine for realistic sensor value generation.

All values are physics-informed approximations, NOT random numbers.
They model real-world water pipeline behavior.
"""
import math
import random
import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PipelineState:
    """
    Represents the physical state of a pipeline segment.
    All base values are calibrated to a residential society water system.
    """
    # Baseline values (realistic residential water system)
    base_flow_lpm: float = 18.0       # L/min normal flow
    base_pressure_bar: float = 2.8    # bar normal pressure
    base_acoustic_rms: float = 0.12   # RMS vibration (0 = silent, >0.5 = leak)
    base_motor_current_a: float = 3.1 # Amps at normal pump load
    base_tank_level: float = 72.0     # % filled
    pump_on: bool = True

    # Leak simulation
    leak_active: bool = False
    leak_magnitude: float = 0.0       # 0.0-1.0 severity
    leak_start_time: Optional[float] = None

    # Sensor failure simulation
    flow_sensor_failed: bool = False
    pressure_sensor_failed: bool = False
    acoustic_sensor_failed: bool = False

    # Internal state
    _noise_seed: float = field(default_factory=lambda: random.random() * 1000)
    _uptime_start: float = field(default_factory=time.time)

    def uptime_seconds(self) -> int:
        return int(time.time() - self._uptime_start)

    def _perlin_noise(self, t: float, freq: float = 0.1, amplitude: float = 1.0) -> float:
        """Simple smooth pseudo-noise for natural signal variation."""
        return amplitude * (
            math.sin(t * freq + self._noise_seed) * 0.6 +
            math.sin(t * freq * 2.7 + self._noise_seed * 0.5) * 0.3 +
            math.sin(t * freq * 0.4 + self._noise_seed * 1.3) * 0.1
        )

    def get_flow_lpm(self, t: float) -> Optional[float]:
        if self.flow_sensor_failed:
            return None  # Sensor failure — return None, not 0

        if not self.pump_on:
            # Pump off: residual flow from tank pressure only
            base = self.base_flow_lpm * 0.15
        else:
            base = self.base_flow_lpm

        # Natural usage variation (tap open/close events)
        variation = self._perlin_noise(t, freq=0.08, amplitude=3.5)
        flow = base + variation

        # Leak adds extra unexplained flow loss
        if self.leak_active:
            leak_time = t - (self.leak_start_time or t)
            # Leak flow ramps up over 3 seconds then stabilizes
            leak_flow = self.leak_magnitude * 12.0 * min(1.0, leak_time / 3.0)
            flow += leak_flow

        return max(0.0, round(flow, 2))

    def get_pressure_bar(self, t: float) -> Optional[float]:
        if self.pressure_sensor_failed:
            return None

        if not self.pump_on:
            # Pressure drops when pump is off
            base = self.base_pressure_bar * 0.55
        else:
            base = self.base_pressure_bar

        variation = self._perlin_noise(t, freq=0.15, amplitude=0.08)
        pressure = base + variation

        # Pressure drops at leak location (Bernoulli effect)
        if self.leak_active:
            leak_time = t - (self.leak_start_time or t)
            drop = self.leak_magnitude * 0.65 * min(1.0, leak_time / 4.0)
            pressure -= drop

        return max(0.0, round(pressure, 3))

    def get_acoustic_rms(self, t: float) -> Optional[float]:
        if self.acoustic_sensor_failed:
            return None

        # Baseline pipe vibration (pump harmonics, water hammer)
        base = self.base_acoustic_rms
        variation = self._perlin_noise(t, freq=0.25, amplitude=0.02)
        acoustic = base + variation

        # Leak creates high-frequency turbulence (clearly elevated RMS)
        if self.leak_active:
            leak_time = t - (self.leak_start_time or t)
            # Acoustic signature ramps up fast (detectable in ~1s)
            leak_acoustic = self.leak_magnitude * 0.55 * min(1.0, leak_time / 1.5)
            # Add turbulence noise
            turbulence = random.gauss(0, 0.04) * self.leak_magnitude
            acoustic += leak_acoustic + abs(turbulence)

        return max(0.0, round(acoustic, 4))

    def get_motor_current_a(self, t: float) -> float:
        if not self.pump_on:
            return 0.0
        base = self.base_motor_current_a
        variation = self._perlin_noise(t, freq=0.05, amplitude=0.15)
        # Leak causes slight motor load increase (pumping harder)
        if self.leak_active:
            base += self.leak_magnitude * 0.4
        return max(0.0, round(base + variation, 2))

    def get_tank_level_percent(self, t: float) -> float:
        # Tank drains slowly during normal operation, refills with pump
        drain_rate = 0.008  # % per second
        if self.pump_on:
            # Pump maintains level
            variation = self._perlin_noise(t, freq=0.02, amplitude=1.5)
            level = self.base_tank_level + variation
        else:
            # Draining
            elapsed = t % 3600  # reset cycle
            level = self.base_tank_level - (drain_rate * elapsed)

        # Leak causes faster drain
        if self.leak_active:
            level -= self.leak_magnitude * 8.0

        return max(0.0, min(100.0, round(level, 1)))

    def trigger_leak(self, magnitude: float = 0.7):
        """Activate a leak scenario."""
        self.leak_active = True
        self.leak_magnitude = max(0.1, min(1.0, magnitude))
        self.leak_start_time = time.time()

    def stop_leak(self):
        self.leak_active = False
        self.leak_magnitude = 0.0
        self.leak_start_time = None

    def pump_startup(self):
        """Simulate pump turning on."""
        self.pump_on = True

    def pump_shutdown(self):
        """Simulate pump turning off."""
        self.pump_on = False

    def fail_sensor(self, sensor: str):
        if sensor == "flow":
            self.flow_sensor_failed = True
        elif sensor == "pressure":
            self.pressure_sensor_failed = True
        elif sensor == "acoustic":
            self.acoustic_sensor_failed = True

    def recover_sensor(self, sensor: str):
        if sensor == "flow":
            self.flow_sensor_failed = False
        elif sensor == "pressure":
            self.pressure_sensor_failed = False
        elif sensor == "acoustic":
            self.acoustic_sensor_failed = False
