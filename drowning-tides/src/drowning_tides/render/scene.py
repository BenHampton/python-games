import moderngl as mgl
import numpy as np

from drowning_tides.config import settings as cfg
from drowning_tides.core.mesh import Mesh
from drowning_tides.render.rain import Rain
from drowning_tides.render.sky import Sky
from drowning_tides.render.water import Water


class Scene:
    """Owns the world objects, renders them into an offscreen FBO, then resolves
    the framebuffer through the painterly post-process pass, then draws UI overlays.
    """

    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx

        self.sky = Sky(app)
        self.water = Water(app)
        self.boat = app.boat
        self.rain = Rain(app)
        self.console = app.console

        # offscreen target for the post pass
        size = (int(cfg.WIN_RES.x), int(cfg.WIN_RES.y))
        self.color_tex = self.ctx.texture(size, 4)
        self.color_tex.filter = (mgl.LINEAR, mgl.LINEAR)
        self.depth_tex = self.ctx.depth_texture(size)
        self.fbo = self.ctx.framebuffer(
            color_attachments=[self.color_tex], depth_attachment=self.depth_tex
        )

        # fullscreen triangle for the post pass
        quad = np.array([-1.0, -1.0, 3.0, -1.0, -1.0, 3.0], dtype='f4')
        self.post_quad = Mesh(self.ctx, app.shader_program.post, quad, '2f', ('in_position',))

    def render(self):
        # --- scene into the offscreen buffer ---
        self.fbo.use()
        self.ctx.clear(cfg.BG_COLOR.x, cfg.BG_COLOR.y, cfg.BG_COLOR.z, 1.0)

        # sky as background: no depth interaction
        self.ctx.disable(mgl.DEPTH_TEST)
        self.sky.render()

        # world geometry
        self.ctx.enable(mgl.DEPTH_TEST)
        self.water.render()
        self.boat.render()

        # rain: depth-tested against the scene but no depth writes, alpha blended
        self.ctx.depth_mask = False
        self.rain.render()
        self.ctx.depth_mask = True

        # --- resolve through the painterly post pass to the screen ---
        self.ctx.screen.use()
        self.ctx.disable(mgl.DEPTH_TEST)
        self.color_tex.use(location=0)
        self.post_quad.render()

        # UI overlays (crisp, after post)
        self.console.render()
