import moderngl as mgl
import numpy as np
import pygame as pg

from drowning_tides.config import settings as cfg


class PauseMenu:
    """A simple centred pause overlay with a Resume button. Rasterised with pygame to a
    GL texture and drawn as a fullscreen quad after the post pass (like the console).
    """

    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        self.program = app.shader_program.console   # textured quad shader (in_position, in_uv)
        self.title_font = pg.font.SysFont('menlo,monospace', 18)
        self.button_font = pg.font.SysFont('menlo,monospace', 24)

        self.active = False
        self._dirty = True

        self.W = int(cfg.WIN_RES.x)
        self.H = int(cfg.WIN_RES.y)
        bw, bh, gap = 240, 56, 18
        cx, cy = self.W // 2, self.H // 2
        self.resume_button = pg.Rect(cx - bw // 2, cy - bh - gap // 2, bw, bh)
        self.quit_button = pg.Rect(cx - bw // 2, cy + gap // 2, bw, bh)

        self._build_quad()
        self.texture = self.ctx.texture((self.W, self.H), 4)
        self.texture.filter = (mgl.LINEAR, mgl.LINEAR)

    def _build_quad(self):
        # fullscreen quad; uv v flipped so the pygame surface (row 0 = top) draws upright
        quad = np.array([
            -1.0, -1.0, 0.0, 1.0,
             1.0, -1.0, 1.0, 1.0,
             1.0,  1.0, 1.0, 0.0,
            -1.0, -1.0, 0.0, 1.0,
             1.0,  1.0, 1.0, 0.0,
            -1.0,  1.0, 0.0, 0.0,
        ], dtype='f4')
        self.vbo = self.ctx.buffer(quad.tobytes())
        self.vao = self.ctx.vertex_array(
            self.program, [(self.vbo, '2f 2f', 'in_position', 'in_uv')], skip_errors=True
        )

    def toggle(self):
        self.active = not self.active
        self._dirty = True

    def click(self, pos):
        """Return 'resume', 'quit', or None for a screen point (top-left origin)."""
        if not self.active:
            return None
        if self.resume_button.collidepoint(pos):
            return 'resume'
        if self.quit_button.collidepoint(pos):
            return 'quit'
        return None

    def _draw_button(self, surf, rect, text, accent):
        pg.draw.rect(surf, (40, 52, 64, 255), rect, border_radius=8)
        pg.draw.rect(surf, accent, rect, width=2, border_radius=8)
        label = self.button_font.render(text, True, (222, 232, 238))
        surf.blit(label, (rect.centerx - label.get_width() // 2,
                          rect.centery - label.get_height() // 2))

    def _rebuild(self):
        surf = pg.Surface((self.W, self.H), pg.SRCALPHA)
        surf.fill((6, 9, 12, 150))                      # dim the frozen scene
        panel = self.resume_button.union(self.quit_button).inflate(140, 150)
        pg.draw.rect(surf, (16, 20, 26, 225), panel, border_radius=10)
        pg.draw.rect(surf, (60, 70, 80, 255), panel, width=2, border_radius=10)

        title = self.title_font.render('PAUSED', True, (150, 165, 175))
        surf.blit(title, (panel.centerx - title.get_width() // 2, panel.top + 22))

        self._draw_button(surf, self.resume_button, 'Resume', (95, 115, 135, 255))
        self._draw_button(surf, self.quit_button, 'Quit', (135, 90, 90, 255))

        self.texture.write(pg.image.tostring(surf, 'RGBA'))
        self._dirty = False

    def render(self):
        if not self.active:
            return
        if self._dirty:
            self._rebuild()
        self.texture.use(location=0)
        self.vao.render()
