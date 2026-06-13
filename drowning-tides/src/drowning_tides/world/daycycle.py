"""Time-of-day cycle.

Drives a normalized day phase `t` in [0,1) and derives everything time-dependent from it:
the sun/moon directions (sun arcs across the sky, moon opposite), a day/night factor, a
star-fade alpha, the key light direction + colour, and an interpolated mood palette
(sky/water/fog colours + sun strength) from `cfg.DAY_KEYFRAMES`. Storms and fog banks are
composed on top of this base palette in `core/shader_program.py`.
"""
import math

from pyglm import glm

from drowning_tides.config import settings as cfg


def _smoothstep(edge0, edge1, x):
    if edge0 == edge1:
        return 0.0
    t = max(0.0, min(1.0, (x - edge0) / (edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)


class Palette:
    __slots__ = (
        'water_color', 'water_color_deep', 'fog_color', 'fog_near', 'fog_far',
        'sky_horizon', 'sky_top', 'sun_strength',
    )

    def __init__(self, **fields):
        for k, v in fields.items():
            setattr(self, k, v)


class DayCycle:
    def __init__(self, t=None, timescale=None):
        self.t = cfg.DAY_START if t is None else (t % 1.0)
        self.timescale = cfg.DAY_TIMESCALE if timescale is None else timescale
        self._recompute()

    # ----------------------------------------------------------------- console hooks
    def set_time(self, t):
        self.t = t % 1.0
        self._recompute()

    # -------------------------------------------------------------------- per-frame
    def update(self, dt):
        if cfg.DAY_LENGTH > 0:
            self.t = (self.t + dt * self.timescale / cfg.DAY_LENGTH) % 1.0
        self._recompute()

    def _recompute(self):
        # sun arcs: a=0 at sunrise (t=0.25), pi/2 at noon (t=0.5), pi at sunset (t=0.75)
        a = (self.t - 0.25) * 2.0 * math.pi
        elev = math.sin(a)
        horiz = math.cos(a)
        self.sun_dir = glm.normalize(glm.vec3(horiz, elev, horiz * cfg.SUN_ARC_TILT))
        self.moon_dir = -self.sun_dir

        self.day_factor = _smoothstep(-0.05, 0.18, self.sun_dir.y)
        self.star_alpha = 1.0 - self.day_factor

        # key light follows whichever body is above the horizon
        self.light_dir = self.sun_dir if self.sun_dir.y >= 0.0 else self.moon_dir
        self.light_color = glm.mix(cfg.MOON_COLOR, cfg.SUN_COLOR, self.day_factor)

        self.palette = self._interp_palette(self.t)

    @staticmethod
    def _interp_palette(t):
        keys = cfg.DAY_KEYFRAMES
        ext_keys = keys + [keys[0]]
        ext_times = [k['t'] for k in keys] + [keys[0]['t'] + 1.0]
        tt = t + 1.0 if t < ext_times[0] else t

        # pick the segment containing tt (ascending keyframes, with wraparound)
        k0, k1, f = keys[0], keys[0], 0.0
        for i in range(len(keys)):
            if ext_times[i] <= tt <= ext_times[i + 1]:
                span = ext_times[i + 1] - ext_times[i]
                f = (tt - ext_times[i]) / span if span > 0 else 0.0
                k0, k1 = ext_keys[i], ext_keys[i + 1]
                break

        def lerp(key):
            return k0[key] + (k1[key] - k0[key]) * f

        return Palette(
            water_color=lerp('water_color'),
            water_color_deep=lerp('water_color_deep'),
            fog_color=lerp('fog_color'),
            fog_near=lerp('fog_near'),
            fog_far=lerp('fog_far'),
            sky_horizon=lerp('sky_horizon'),
            sky_top=lerp('sky_top'),
            sun_strength=lerp('sun_strength'),
        )
