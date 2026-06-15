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


class RainState:
    """Rain on its own scheduler, only loosely tied to storms. It rains on a random cadence
    even in calm daytime (drizzle..moderate shower), and a storm usually — but not always —
    drives its own heavier rain on top. Exposes a smoothed `intensity` (0..1). Same
    clear->in->hold->out phase shape as FogBank, with a `storm_rain` floor folded in each frame.
    """

    def __init__(self):
        self.intensity = 0.0
        self.target = 0.0
        self.peak = 0.0
        self.buildup = self.hold = self.ease = 0.0
        self._enter('clear')

    def _enter(self, phase):
        self.phase = phase
        self.elapsed = 0.0
        if phase == 'clear':
            self.duration = random.uniform(*cfg.RAIN_CALM_RANGE)
        elif phase == 'in':
            self.peak = random.uniform(*cfg.RAIN_PEAK_RANGE)
            self.buildup = random.uniform(*cfg.RAIN_BUILDUP_RANGE)
            self.hold = random.uniform(*cfg.RAIN_HOLD_RANGE)
            self.ease = random.uniform(*cfg.RAIN_EASE_RANGE)
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

    def update(self, dt, storm_rain):
        """Advance the independent schedule, then show the heavier of (scheduled, storm-driven)
        rain so storms add rain without erasing a calm-day shower."""
        self.elapsed += dt
        scheduled = 0.0
        if self.phase == 'kill':
            self.target = max(0.0, self.target - cfg.RAIN_KILL_RATE * dt)
            if self.target <= 1e-3:
                self._enter('clear')
        else:
            if self.phase == 'clear':
                if self.elapsed >= self.duration:
                    self._enter('in')
            elif self.phase == 'in':
                p = self.elapsed / self.duration if self.duration > 0 else 1.0
                scheduled = self.peak * _smoothstep(p)
                if self.elapsed >= self.duration:
                    self._enter('hold')
            elif self.phase == 'hold':
                scheduled = self.peak
                if self.elapsed >= self.duration:
                    self._enter('out')
            elif self.phase == 'out':
                p = self.elapsed / self.duration if self.duration > 0 else 1.0
                scheduled = self.peak * (1.0 - _smoothstep(p))
                if self.elapsed >= self.duration:
                    self._enter('clear')
            self.target = min(1.0, max(scheduled, storm_rain))

        track = 1.0 - math.exp(-cfg.RAIN_TRACK_LERP * dt)
        self.intensity += (self.target - self.intensity) * track


class Weather:
    """Drives a single global storm_intensity (0..1) via a real-weather scheduler, plus a slowly
    wandering wind direction/strength. Waves, mood lighting and the boat current read from
    storm_intensity. Rain is its own loosely-coupled RainState (see rain_intensity) — it can rain
    in calm daytime, and storms usually but not always bring rain. Console commands override both.
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

        # rain: its own scheduler; storms usually (but not always) bring their own rain
        self.rain = RainState()
        self._storm_rain_gain = 0.0     # this storm's rain heaviness (0 = a dry storm)

        # cloud cover (0..1): wanders through the day, forced overcast by storms
        self.cloud_cover = 0.4
        self._cloud_target = random.uniform(0.2, 0.7)
        self._cloud_timer = random.uniform(*cfg.CLOUD_WANDER_RANGE)

        # lightning: a decaying flash (with flicker spikes) + an occasional drawn bolt
        self.lightning = 0.0
        self._flicker_spikes = 0
        self._flicker_timer = 0.0
        self.bolt_active = False
        self.bolt_seed = 0
        self.bolt_life = 0.0

        self._enter('calm')

    @property
    def fog_intensity(self):
        return self.fog.intensity

    @property
    def rain_intensity(self):
        return self.rain.intensity

    # ------------------------------------------------------------------ scheduler
    def _enter(self, phase):
        self.phase = phase
        self.elapsed = 0.0
        if phase == 'calm':
            self.duration = random.uniform(*cfg.WEATHER_CALM_RANGE)
        elif phase == 'buildup':
            self.peak = random.uniform(*cfg.WEATHER_PEAK_RANGE)
            self.duration = random.uniform(*cfg.WEATHER_BUILDUP_RANGE)
            # decide up front whether this storm is a rainy one (most are) or a dry, windy blow
            if random.random() < cfg.STORM_RAIN_CHANCE:
                self._storm_rain_gain = random.uniform(*cfg.STORM_RAIN_GAIN)
            else:
                self._storm_rain_gain = 0.0
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

    def start_rain(self):
        self.rain.start()

    def kill_rain(self):
        self.rain.kill()

    def strike(self):
        """Force a lightning flash + bolt now (used by the dev console)."""
        self._flicker_spikes = random.randint(2, 3)
        self._flicker_timer = 0.0
        self.bolt_active = True
        self.bolt_seed = random.randint(0, 1 << 30)
        self.bolt_life = cfg.BOLT_LIFETIME

    def set_clouds(self, amount):
        self._cloud_target = max(0.0, min(1.0, amount))
        self._cloud_timer = random.uniform(*cfg.CLOUD_WANDER_RANGE)

    # ------------------------------------------------------------------ clouds + lightning
    def _update_clouds(self, dt):
        self._cloud_timer -= dt
        if self._cloud_timer <= 0.0:
            self._cloud_target = random.uniform(0.15, 0.85)
            self._cloud_timer = random.uniform(*cfg.CLOUD_WANDER_RANGE)
        target = max(self._cloud_target, self.storm_intensity)
        self.cloud_cover += (target - self.cloud_cover) * (1.0 - math.exp(-cfg.CLOUD_EASE * dt))

    def _update_lightning(self, dt):
        self.lightning *= math.exp(-cfg.LIGHTNING_DECAY * dt)
        if self._flicker_spikes > 0:
            self._flicker_timer -= dt
            if self._flicker_timer <= 0.0:
                self.lightning = 1.0
                self._flicker_spikes -= 1
                self._flicker_timer = random.uniform(0.04, 0.12)
        elif self.storm_intensity > 0.3:
            if random.random() < cfg.LIGHTNING_RATE * self.storm_intensity * dt:
                self._flicker_spikes = random.randint(2, 3)
                self._flicker_timer = 0.0
                if random.random() < cfg.BOLT_CHANCE:
                    self.bolt_active = True
                    self.bolt_seed = random.randint(0, 1 << 30)
                    self.bolt_life = cfg.BOLT_LIFETIME
        if self.bolt_active:
            self.bolt_life -= dt
            if self.bolt_life <= 0.0:
                self.bolt_active = False

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

        # rain: a rainy storm drives rain with its intensity; the rain scheduler runs regardless
        self.rain.update(dt, self.storm_intensity * self._storm_rain_gain)

        # slowly wander the wind direction
        self.wind_angle += random.uniform(-1.0, 1.0) * cfg.WIND_WANDER_RATE * dt
        self.wind_dir = glm.vec2(math.cos(self.wind_angle), math.sin(self.wind_angle))
        self.wind_strength = cfg.WIND_MAX_STRENGTH * self.storm_intensity

        self._update_clouds(dt)
        self._update_lightning(dt)

    # ----------------------------------------------------------------- derived data
    def current_vector(self):
        """World-space push on the boat from the wind-driven current (xz in a vec3)."""
        c = cfg.CURRENT_PUSH * self.storm_intensity
        return glm.vec3(self.wind_dir.x * c, 0.0, self.wind_dir.y * c)
