"""Lightning bolt: a jagged line-strip rebuilt each strike, drawn bright + additive so the
bloom pass makes it glow. Visibility/brightness follow `weather.bolt_active` / `bolt_life`.
"""
import math
import random

import moderngl as mgl
import numpy as np

from drowning_tides.config import settings as cfg


class Bolt:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        self.program = app.shader_program.bolt
        self._seed = None
        self.vbo = None
        self.vao = None

    def _build(self, seed, cam):
        rng = random.Random(seed)
        ang = rng.uniform(0.0, math.tau)
        dx, dz = math.cos(ang), math.sin(ang)
        px, pz = -dz, dx                      # perpendicular, for lateral jitter
        top_y = rng.uniform(160.0, 240.0)
        base = rng.uniform(120.0, 320.0)
        lateral = 0.0
        pts = []
        n = cfg.BOLT_SEGMENTS
        for i in range(n + 1):
            f = i / n
            r = base * (0.5 + 0.5 * f)
            lateral += rng.uniform(-1.0, 1.0) * 12.0
            x = cam.x + dx * r + px * lateral
            z = cam.z + dz * r + pz * lateral
            pts.append((x, top_y * (1.0 - f), z))
        arr = np.array(pts, dtype='f4')

        if self.vao is not None:
            self.vao.release()
            self.vbo.release()
        self.vbo = self.ctx.buffer(arr.tobytes())
        self.vao = self.ctx.vertex_array(
            self.program, [(self.vbo, '3f', 'in_position')], skip_errors=True
        )

    def render(self):
        w = self.app.weather
        if not w.bolt_active:
            return
        if w.bolt_seed != self._seed:
            self._seed = w.bolt_seed
            self._build(self._seed, self.app.camera.position)
        self.program['m_view'].write(self.app.camera.m_view)
        self.program['u_alpha'] = max(0.0, w.bolt_life / cfg.BOLT_LIFETIME)
        self.vao.render(mode=mgl.LINE_STRIP)
