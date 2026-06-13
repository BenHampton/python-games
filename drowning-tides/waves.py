import math
import numpy as np
from pyglm import glm
from settings import *


class WaveField:
    """A small fixed set of Gerstner wave components. Parameters are recomputed from
    the wind direction + storm intensity, then evaluated identically on the GPU
    (water.vert) and on the CPU (boat buoyancy) so the boat sits on the visible sea.
    """

    def __init__(self):
        self.n = N_WAVES
        # static per-component data
        self.k = [2.0 * math.pi / L for L in WAVE_WAVELENGTHS]      # wavenumbers
        self.w = [math.sqrt(GRAVITY * k) for k in self.k]          # angular speeds
        # dynamic (recomputed each frame)
        self.dirs = [(1.0, 0.0)] * self.n
        self.amp = [0.0] * self.n
        self.q = [0.0] * self.n
        self.recompute(glm.vec2(1.0, 0.0), 0.0)

    def recompute(self, wind_dir, intensity):
        wd = glm.normalize(wind_dir) if glm.length(wind_dir) > 1e-6 else glm.vec2(1, 0)
        base = math.atan2(wd.y, wd.x)

        amp_scale = WAVE_CALM_AMP + (WAVE_STORM_AMP - WAVE_CALM_AMP) * intensity
        amps = [amp_scale * r for r in WAVE_AMP_RATIOS]
        total = sum(amps)
        if total > WAVE_MAX_AMPLITUDE:
            s = WAVE_MAX_AMPLITUDE / total
            amps = [a * s for a in amps]

        for i in range(self.n):
            off = ((i / (self.n - 1)) - 0.5) * 2.0 * WAVE_DIR_SPREAD if self.n > 1 else 0.0
            ang = base + off
            self.dirs[i] = (math.cos(ang), math.sin(ang))
            self.amp[i] = amps[i]
            k = self.k[i]
            self.q[i] = WAVE_STEEPNESS / (k * amps[i] * self.n) if amps[i] > 1e-6 else 0.0

    # ------------------------------------------------------------------ CPU sample
    def sample(self, x, z, t):
        """Return (height, normal) at world (x, z) and time t. Matches water.vert."""
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
