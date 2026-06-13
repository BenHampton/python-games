import math
import random

from pyglm import glm

from drowning_tides.config import settings as cfg


def _smoothstep(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


class FogBank:
    """Rolling fog, independent of storms and time of day. Scheduled like a storm
    (clear gap -> roll in -> hold -> fade out) and exposes a smoothed `intensity`
    (0..1). A single bank's active time is capped at cfg.FOG_MAX_DURATION.
    """

    def __init__(self):
        self.intensity = 0.0
        self.target = 0.0
        self.peak = 0.0
        self._enter('clear')

    def _enter(self, phase):
        self.phase = phase
        self.elapsed = 0.0
        if phase == 'clear':
            self.duration = random.uniform(*cfg.FOG_CALM_RANGE)
        elif phase == 'in':
            self.peak = random.uniform(*cfg.FOG_PEAK_RANGE)
            self.buildup = random.uniform(*cfg.FOG_BUILDUP_RANGE)
            self.hold = random.uniform(*cfg.FOG_HOLD_RANGE)
            self.ease = random.uniform(*cfg.FOG_EASE_RANGE)
            # cap total active time (revisit: make durations more realistic later)
            if self.buildup + self.hold + self.ease > cfg.FOG_MAX_DURATION:
                self.hold = max(0.0, cfg.FOG_MAX_DURATION - self.buildup - self.ease)
            self.duration = self.buildup
        elif phase == 'hold':
            self.duration = self.hold
        elif phase == 'out':
            self.duration = self.ease
        elif phase == 'kill':
            self.duration = 0.0

    def start(self):
        self._enter('in')

    def kill(self):
        self._enter('kill')

    def update(self, dt):
        self.elapsed += dt
        if self.phase == 'kill':
            self.target = max(0.0, self.target - cfg.FOG_KILL_RATE * dt)
            if self.target <= 1e-3:
                self._enter('clear')
        elif self.phase == 'clear':
            self.target = 0.0
            if self.elapsed >= self.duration:
                self._enter('in')
        elif self.phase == 'in':
            p = self.elapsed / self.duration if self.duration > 0 else 1.0
            self.target = self.peak * _smoothstep(p)
            if self.elapsed >= self.duration:
                self._enter('hold')
        elif self.phase == 'hold':
            self.target = self.peak
            if self.elapsed >= self.duration:
                self._enter('out')
        elif self.phase == 'out':
            p = self.elapsed / self.duration if self.duration > 0 else 1.0
            self.target = self.peak * (1.0 - _smoothstep(p))
            if self.elapsed >= self.duration:
                self._enter('clear')

        # roll/fade: smooth the visible intensity toward its target
        self.intensity += (self.target - self.intensity) * (1.0 - math.exp(-3.0 * dt))


class Weather:
    """Drives a single global storm_intensity (0..1) via a real-weather scheduler,
    plus a slowly wandering wind direction/strength. Console commands override the
    scheduler. Everything else (waves, rain, mood lighting, boat current) reads from
    this.
    """

    PHASES = ('calm', 'buildup', 'hold', 'ease')

    def __init__(self):
        self.storm_intensity = 0.0
        self.target = 0.0
        self.peak = 0.0

        self.wind_angle = math.atan2(cfg.WIND_START_DIR.y, cfg.WIND_START_DIR.x)
        self.wind_dir = glm.vec2(math.cos(self.wind_angle), math.sin(self.wind_angle))
        self.wind_strength = 0.0

        self.fog = FogBank()

        self._enter('calm')

    @property
    def fog_intensity(self):
        return self.fog.intensity

    # ------------------------------------------------------------------ scheduler
    def _enter(self, phase):
        self.phase = phase
        self.elapsed = 0.0
        if phase == 'calm':
            self.duration = random.uniform(*cfg.WEATHER_CALM_RANGE)
        elif phase == 'buildup':
            self.peak = random.uniform(*cfg.WEATHER_PEAK_RANGE)
            self.duration = random.uniform(*cfg.WEATHER_BUILDUP_RANGE)
        elif phase == 'hold':
            self.duration = random.uniform(*cfg.WEATHER_HOLD_RANGE)
        elif phase == 'ease':
            self.duration = random.uniform(*cfg.WEATHER_EASE_RANGE)
        elif phase == 'kill':
            self.duration = 0.0

    def _advance(self):
        order = {'calm': 'buildup', 'buildup': 'hold', 'hold': 'ease', 'ease': 'calm'}
        self._enter(order[self.phase])

    # --------------------------------------------------------------- console hooks
    def start_storm(self):
        self._enter('buildup')

    def kill_storm(self):
        self._enter('kill')   # rapidly decays target to 0, then returns to calm

    def start_fog(self):
        self.fog.start()

    def kill_fog(self):
        self.fog.kill()

    # -------------------------------------------------------------------- per-frame
    def update(self, dt):
        self.fog.update(dt)
        self.elapsed += dt

        if self.phase == 'kill':
            self.target = max(0.0, self.target - cfg.STORM_KILL_RATE * dt)
            if self.target <= 1e-3:
                self._enter('calm')
        else:
            p = self.elapsed / self.duration if self.duration > 0 else 1.0
            if self.phase == 'calm':
                self.target = 0.0
            elif self.phase == 'buildup':
                self.target = self.peak * _smoothstep(p)
            elif self.phase == 'hold':
                self.target = self.peak
            elif self.phase == 'ease':
                self.target = self.peak * (1.0 - _smoothstep(p))
            if self.elapsed >= self.duration:
                self._advance()

        # smooth the visible intensity toward its target
        self.storm_intensity += (self.target - self.storm_intensity) * (1.0 - math.exp(-4.0 * dt))

        # slowly wander the wind direction
        self.wind_angle += random.uniform(-1.0, 1.0) * cfg.WIND_WANDER_RATE * dt
        self.wind_dir = glm.vec2(math.cos(self.wind_angle), math.sin(self.wind_angle))
        self.wind_strength = cfg.WIND_MAX_STRENGTH * self.storm_intensity

    # ----------------------------------------------------------------- derived data
    def current_vector(self):
        """World-space push on the boat from the wind-driven current (xz in a vec3)."""
        c = cfg.CURRENT_PUSH * self.storm_intensity
        return glm.vec3(self.wind_dir.x * c, 0.0, self.wind_dir.y * c)
