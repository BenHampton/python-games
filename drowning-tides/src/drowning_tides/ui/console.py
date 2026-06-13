import moderngl as mgl
import numpy as np
import pygame as pg

from drowning_tides.config import settings as cfg


class Console:
    """In-game dev console. Backtick toggles it (handled in main). While open it
    captures typed text; Enter runs a command. Text is rasterized with pygame, then
    uploaded to a GL texture and drawn as a bottom overlay quad after the post pass.
    """

    BAR_H = cfg.CONSOLE_HEIGHT * 2   # input line + a feedback line above it

    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        self.program = app.shader_program.console
        self.font = pg.font.SysFont('menlo,monospace', cfg.CONSOLE_FONT_SIZE)

        self.active = False
        self.text = ''
        self.message = ''
        self._dirty = True

        # command table (extend here for /storm 0.7, thunder, etc.)
        self.commands = {
            '/storm-on': self._cmd_storm_on,
            '/storm-kill': self._cmd_storm_kill,
        }

        self.W = int(cfg.WIN_RES.x)
        self._build_quad()
        self.texture = self.ctx.texture((self.W, self.BAR_H), 4)
        self.texture.filter = (mgl.LINEAR, mgl.LINEAR)

    def _build_quad(self):
        frac = 2.0 * self.BAR_H / cfg.WIN_RES.y      # bar height in NDC
        y0, y1 = -1.0, -1.0 + frac
        # pos.xy, uv (v=0 at top row of the surface)
        quad = np.array([
            -1.0, y0, 0.0, 1.0,
             1.0, y0, 1.0, 1.0,
             1.0, y1, 1.0, 0.0,
            -1.0, y0, 0.0, 1.0,
             1.0, y1, 1.0, 0.0,
            -1.0, y1, 0.0, 0.0,
        ], dtype='f4')
        self.vbo = self.ctx.buffer(quad.tobytes())
        self.vao = self.ctx.vertex_array(
            self.program, [(self.vbo, '2f 2f', 'in_position', 'in_uv')], skip_errors=True
        )

    # ---------------------------------------------------------------------- input
    def toggle(self):
        self.active = not self.active
        self._dirty = True

    def handle_key(self, event):
        if event.key == pg.K_RETURN:
            self._run()
        elif event.key == pg.K_BACKSPACE:
            self.text = self.text[:-1]
        elif event.key == pg.K_ESCAPE:
            self.active = False
        else:
            ch = event.unicode
            if ch and ch.isprintable() and ch != '`':
                self.text += ch
        self._dirty = True

    def _run(self):
        cmd = self.text.strip()
        self.text = ''
        if not cmd:
            return
        name = cmd.split()[0]
        fn = self.commands.get(name)
        if fn:
            fn()
        else:
            self.message = f'unknown command: {name}'

    def _cmd_storm_on(self):
        self.app.weather.start_storm()
        self.message = 'storm rolling in...'

    def _cmd_storm_kill(self):
        self.app.weather.kill_storm()
        self.message = 'storm clearing...'

    # --------------------------------------------------------------------- render
    def _rebuild_texture(self):
        surf = pg.Surface((self.W, self.BAR_H), pg.SRCALPHA)
        # input bar background
        pg.draw.rect(
            surf, cfg.CONSOLE_BG_COLOR, (0, cfg.CONSOLE_HEIGHT, self.W, cfg.CONSOLE_HEIGHT)
        )
        line = cfg.CONSOLE_PROMPT + self.text + '_'
        ts = self.font.render(line, True, cfg.CONSOLE_TEXT_COLOR)
        surf.blit(ts, (8, cfg.CONSOLE_HEIGHT + (cfg.CONSOLE_HEIGHT - ts.get_height()) // 2))
        # feedback line
        if self.message:
            pg.draw.rect(surf, (8, 11, 14, 150), (0, 0, self.W, cfg.CONSOLE_HEIGHT))
            ms = self.font.render(self.message, True, (150, 165, 170))
            surf.blit(ms, (8, (cfg.CONSOLE_HEIGHT - ms.get_height()) // 2))
        self.texture.write(pg.image.tostring(surf, 'RGBA'))
        self._dirty = False

    def render(self):
        if not self.active:
            return
        if self._dirty:
            self._rebuild_texture()
        self.texture.use(location=0)
        self.vao.render()
