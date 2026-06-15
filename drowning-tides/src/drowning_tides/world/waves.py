import math

import numpy as np
from pyglm import glm

from drowning_tides.config import settings as cfg


class WaveField:
    """A small fixed set of Gerstner wave components. Parameters are recomputed from
    the wind direction + storm intensity, then evaluated identically on the GPU
    (water.vert) and on the CPU (boat buoyancy) so the boat sits on the visible sea.
    """

    def __init__(self):
        self.n = cfg.N_WAVES
        # static per-component data
        self.k = [2.0 * math.pi / L for L in cfg.WAVE_WAVELENGTHS]      # wavenumbers
        self.w = [math.sqrt(cfg.GRAVITY * k) for k in self.k]          # angular speeds
        # dynamic (recomputed each frame)
        self.dirs = [(1.0, 0.0)] * self.n
        self.amp = [0.0] * self.n
        self.q = [0.0] * self.n
        self.recompute(glm.vec2(1.0, 0.0), 0.0)

    def recompute(self, wind_dir, intensity):
        wd = glm.normalize(wind_dir) if glm.length(wind_dir) > 1e-6 else glm.vec2(1, 0)
        base = math.atan2(wd.y, wd.x)

        amp_scale = cfg.WAVE_CALM_AMP + (cfg.WAVE_STORM_AMP - cfg.WAVE_CALM_AMP) * intensity
        amps = [amp_scale * r for r in cfg.WAVE_AMP_RATIOS]
        total = sum(amps)
        if total > cfg.WAVE_MAX_AMPLITUDE:
            s = cfg.WAVE_MAX_AMPLITUDE / total
            amps = [a * s for a in amps]

        for i in range(self.n):
            off = ((i / (self.n - 1)) - 0.5) * 2.0 * cfg.WAVE_DIR_SPREAD if self.n > 1 else 0.0
            ang = base + off
            self.dirs[i] = (math.cos(ang), math.sin(ang))
            self.amp[i] = amps[i]
            k = self.k[i]
            self.q[i] = cfg.WAVE_STEEPNESS / (k * amps[i] * self.n) if amps[i] > 1e-6 else 0.0

    # ------------------------------------------------------------------ CPU sample
    def sample(self, x, z, t):
        """Return (height, normal) at world (x, z) and time t. Matches water.vert (incl. the
        distance-from-town shelter gain)."""
        height = 0.0
        nx = nz = 0.0
        ny_sub = 0.0
        for i in range(self.n):
            dx, dz = self.dirs[i]
            k = self.k[i]
            a = self.amp[i]
            phase = k * (dx * x + dz * z) - self.w[i] * t
            c = math.cos(phase)
            s = math.sin(phase)
            height += a * s
            wa = k * a
            nx += dx * wa * c
            nz += dz * wa * c
            ny_sub += self.q[i] * wa * s
        g = shelter_gain(x, z)                       # rougher further from the town
        height *= g
        nx *= g
        nz *= g
        ny_sub *= g
        normal = glm.normalize(glm.vec3(-nx, 1.0 - ny_sub, -nz))
        return height, normal

    # ------------------------------------------------------------- shader uniforms
    def write_uniforms(self, prog, t):
        dirs = np.array(self.dirs, dtype='f4')                 # (n, 2)
        prog['u_wave_dir'].write(dirs.tobytes())
        prog['u_wave_k'].write(np.array(self.k, dtype='f4').tobytes())
        prog['u_wave_w'].write(np.array(self.w, dtype='f4').tobytes())
        prog['u_wave_amp'].write(np.array(self.amp, dtype='f4').tobytes())
        prog['u_wave_q'].write(np.array(self.q, dtype='f4').tobytes())
        prog['u_time'] = t
        # distance-from-town shelter gain (must match shelter_gain on the CPU)
        prog['u_shelter_center'] = (cfg.SHELTER_CENTER.x, cfg.SHELTER_CENTER.y)
        prog['u_shelter'] = (cfg.SHELTER_R0, cfg.SHELTER_R1, cfg.SHELTER_MIN, cfg.SHELTER_MAX)


def shelter_gain(x, z):
    """Wave-amplitude multiplier at world (x, z): small near the town (sheltered harbor), rising
    to full out at sea. Mirrors the gain in shaders/water.vert (parity invariant)."""
    d = math.hypot(x - cfg.SHELTER_CENTER.x, z - cfg.SHELTER_CENTER.y)
    t = min(1.0, max(0.0, (d - cfg.SHELTER_R0) / (cfg.SHELTER_R1 - cfg.SHELTER_R0)))
    s = t * t * (3.0 - 2.0 * t)                              # smoothstep (matches GLSL)
    return cfg.SHELTER_MIN + (cfg.SHELTER_MAX - cfg.SHELTER_MIN) * s
