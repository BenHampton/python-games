import moderngl as mgl
import numpy as np
from pyglm import glm

from drowning_tides.config import settings as cfg
from drowning_tides.core.mesh import Mesh
from drowning_tides.render.lightning import Bolt
from drowning_tides.render.rain import Rain
from drowning_tides.render.sky import Sky
from drowning_tides.render.water import Water


class Scene:
    """Owns the world objects, renders them into an offscreen HDR buffer, extracts a
    bloom, then resolves through the painterly + filmic post pass, then draws UI overlays.
    """

    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        sp = app.shader_program

        self.sky = Sky(app)
        self.water = Water(app)
        self.boat = app.boat
        self.rain = Rain(app)
        self.bolt = Bolt(app)
        self.console = app.console

        size = (int(cfg.WIN_RES.x), int(cfg.WIN_RES.y))
        # opaque pass target (HDR f2 so bright sky/glints exceed 1.0 for bloom + tonemapping)
        self.opaque_color = self.ctx.texture(size, 4, dtype='f2')
        self.opaque_color.filter = (mgl.LINEAR, mgl.LINEAR)
        self.depth_tex = self.ctx.depth_texture(size)
        self.depth_tex.compare_func = ''     # sample raw depth, not shadow-compare
        self.opaque_fbo = self.ctx.framebuffer(
            color_attachments=[self.opaque_color], depth_attachment=self.depth_tex
        )
        # final scene target: opaque copy + transparent water composited on top
        self.scene_color = self.ctx.texture(size, 4, dtype='f2')
        self.scene_color.filter = (mgl.LINEAR, mgl.LINEAR)
        self.scene_fbo = self.ctx.framebuffer(color_attachments=[self.scene_color])

        # half-res ping-pong buffers for the bloom blur
        bw, bh = size[0] // 2, size[1] // 2
        self.bloom_texel = (1.0 / bw, 1.0 / bh)
        self.bloom_a = self._bloom_tex((bw, bh))
        self.bloom_b = self._bloom_tex((bw, bh))
        self.bloom_fbo_a = self.ctx.framebuffer(color_attachments=[self.bloom_a])
        self.bloom_fbo_b = self.ctx.framebuffer(color_attachments=[self.bloom_b])

        # half-res god-ray buffer (crepuscular light shafts from the sun)
        self.godray_tex = self._bloom_tex((bw, bh))
        self.godray_fbo = self.ctx.framebuffer(color_attachments=[self.godray_tex])
        self.godrays = sp.godrays

        self.bright = sp.get_program('bright')
        self.blur = sp.get_program('blur')
        self.bright['u_scene'] = 0
        self.blur['u_tex'] = 0

        tri = np.array([-1.0, -1.0, 3.0, -1.0, -1.0, 3.0], dtype='f4')
        self.post_quad = Mesh(self.ctx, sp.post, tri, '2f', ('in_position',))
        self.bright_quad = Mesh(self.ctx, self.bright, tri, '2f', ('in_position',))
        self.blur_quad = Mesh(self.ctx, self.blur, tri, '2f', ('in_position',))
        self.godray_quad = Mesh(self.ctx, self.godrays, tri, '2f', ('in_position',))

    def _bloom_tex(self, size):
        t = self.ctx.texture(size, 4, dtype='f2')
        t.filter = (mgl.LINEAR, mgl.LINEAR)
        t.repeat_x = t.repeat_y = False
        return t

    def render(self):
        # --- opaque pass: sky + land/boat into opaque_color (+ depth) ---
        self.opaque_fbo.use()
        self.ctx.clear(cfg.BG_COLOR.x, cfg.BG_COLOR.y, cfg.BG_COLOR.z, 1.0)

        self.ctx.disable(mgl.DEPTH_TEST)
        self.sky.render()

        self.ctx.enable(mgl.DEPTH_TEST)
        self.app.islands.render(self.app.camera)
        self.boat.render()

        # seed the final buffer with the opaque scene, then composite transparent water on top
        self.ctx.copy_framebuffer(self.scene_fbo, self.opaque_fbo)
        self.scene_fbo.use()
        self.ctx.disable(mgl.DEPTH_TEST)
        self.opaque_color.use(location=0)   # u_scene  (seabed behind the water, for refraction)
        self.depth_tex.use(location=1)      # u_depth  (scene depth, for water thickness)
        self.water.render()
        self.rain.render()
        self.bolt.render()

        # --- bloom: bright-pass then separable blur ping-pong at half res ---
        self.bloom_fbo_a.use()
        self.bright['u_threshold'] = cfg.BLOOM_THRESHOLD
        self.scene_color.use(location=0)
        self.bright_quad.render()
        for _ in range(cfg.BLOOM_PASSES):
            self.bloom_fbo_b.use()
            self.bloom_a.use(location=0)
            self.blur['u_dir'] = (self.bloom_texel[0], 0.0)
            self.blur_quad.render()
            self.bloom_fbo_a.use()
            self.bloom_b.use(location=0)
            self.blur['u_dir'] = (0.0, self.bloom_texel[1])
            self.blur_quad.render()

        # --- god rays: radial light shafts from the sun (occluded by geometry) ---
        self.godray_fbo.use()
        sun_uv, intensity = self._sun_screen()
        self.godrays['u_sun_uv'] = sun_uv
        self.godrays['u_intensity'] = intensity
        self.scene_color.use(location=0)
        self.godray_quad.render()

        # --- composite (painterly + bloom + god rays + filmic grade) to the screen ---
        self.ctx.screen.use()
        self.scene_color.use(location=0)
        self.bloom_a.use(location=1)
        self.godray_tex.use(location=2)
        self.post_quad.render()

        # UI overlays (crisp, after post)
        self.console.render()

    def _sun_screen(self):
        """Sun screen-space position + god-ray intensity (0 when sun down / overcast / behind)."""
        cam = self.app.camera
        day = self.app.daycycle
        sun_world = cam.position + day.sun_dir * 1000.0
        clip = cam.m_proj * cam.m_view * glm.vec4(sun_world, 1.0)
        if clip.w <= 0.0:
            return (0.5, 0.5), 0.0
        uv = (clip.x / clip.w * 0.5 + 0.5, clip.y / clip.w * 0.5 + 0.5)
        sun_up = max(0.0, min(1.0, day.sun_dir.y / 0.25))
        gate = sun_up * (1.0 - 0.7 * self.app.weather.cloud_cover)
        return uv, cfg.GODRAY_INTENSITY * gate
