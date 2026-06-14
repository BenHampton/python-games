import moderngl as mgl
import numpy as np
import pygame as pg

from drowning_tides.config import settings as cfg


class Hud:
    """Transient bottom-centre message line (fishing results, dialogue). Rasterised with
    pygame to a GL texture and drawn as a fullscreen quad after the post pass."""

    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        self.program = app.shader_program.console
        self.font = pg.font.SysFont('menlo,monospace', 22)

        self.message = ''      # timed (fishing/dialogue)
        self.timer = 0.0
        self.prompt = ''       # persistent (e.g. "Press E to dock")
        self._dirty = True
        self.W = int(cfg.WIN_RES.x)
        self.H = int(cfg.WIN_RES.y)

        quad = np.array([
            -1.0, -1.0, 0.0, 1.0,  1.0, -1.0, 1.0, 1.0,  1.0, 1.0, 1.0, 0.0,
            -1.0, -1.0, 0.0, 1.0,  1.0,  1.0, 1.0, 0.0, -1.0, 1.0, 0.0, 0.0,
        ], dtype='f4')
        self.vbo = self.ctx.buffer(quad.tobytes())
        self.vao = self.ctx.vertex_array(
            self.program, [(self.vbo, '2f 2f', 'in_position', 'in_uv')], skip_errors=True
        )
        self.texture = self.ctx.texture((self.W, self.H), 4)
        self.texture.filter = (mgl.LINEAR, mgl.LINEAR)

    def show(self, text, duration=3.0):
        self.message = text
        self.timer = duration
        self._dirty = True

    def set_prompt(self, text):
        if text != self.prompt:
            self.prompt = text
            self._dirty = True

    def update(self, dt):
        if self.timer > 0.0:
            self.timer -= dt
            if self.timer <= 0.0:
                self.message = ''
                self._dirty = True

    def _line(self, surf, text, y_frac, color):
        ts = self.font.render(text, True, color)
        pad = 14
        rect = pg.Rect(0, 0, ts.get_width() + pad * 2, ts.get_height() + pad)
        rect.center = (self.W // 2, int(self.H * y_frac))
        pg.draw.rect(surf, (10, 14, 18, 200), rect, border_radius=8)
        surf.blit(ts, (rect.centerx - ts.get_width() // 2, rect.centery - ts.get_height() // 2))

    def _rebuild(self):
        surf = pg.Surface((self.W, self.H), pg.SRCALPHA)
        if self.prompt:
            self._line(surf, self.prompt, 0.70, (210, 220, 228))
        if self.message:
            self._line(surf, self.message, 0.82, (230, 236, 240))
        self.texture.write(pg.image.tostring(surf, 'RGBA'))
        self._dirty = False

    def render(self):
        if not self.message and not self.prompt:
            return
        if self._dirty:
            self._rebuild()
        self.texture.use(location=0)
        self.vao.render()
