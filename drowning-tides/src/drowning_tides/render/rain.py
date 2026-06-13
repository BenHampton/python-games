import moderngl as mgl
import numpy as np

from drowning_tides.config import settings as cfg


class Rain:
    """Instanced rain: one line streak drawn RAIN_COUNT times, each with a random
    offset inside a box that follows the camera. The vertex shader animates the fall,
    slants streaks along the wind, and wraps drops inside the box so it tiles as the
    camera moves. Density rides on storm_intensity via the streak alpha.
    """

    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        self.program = app.shader_program.rain

        # base streak: two endpoints, in_along = 0 (top) .. 1 (bottom)
        base = np.array([0.0, 1.0], dtype='f4')
        self.base_vbo = self.ctx.buffer(base.tobytes())

        box = cfg.RAIN_BOX
        offsets = (np.random.rand(cfg.RAIN_COUNT, 3).astype('f4') * 2.0 - 1.0)
        offsets *= np.array([box.x, box.y, box.z], dtype='f4')
        self.inst_vbo = self.ctx.buffer(offsets.tobytes())

        self.vao = self.ctx.vertex_array(
            self.program,
            [(self.base_vbo, '1f', 'in_along'),
             (self.inst_vbo, '3f/i', 'in_offset')],
            skip_errors=True,
        )

        # constant uniforms
        self.program['u_box'] = (box.x, box.y, box.z)
        self.program['u_fall'] = cfg.RAIN_FALL_SPEED
        self.program['u_streak_len'] = cfg.RAIN_STREAK_LEN
        self.program['u_rain_color'] = (cfg.RAIN_COLOR.x, cfg.RAIN_COLOR.y, cfg.RAIN_COLOR.z)

    def render(self):
        weather = self.app.weather
        alpha = cfg.RAIN_MAX_ALPHA * weather.storm_intensity
        if alpha < 0.01:
            return

        cam = self.app.camera.position
        wind = weather.wind_dir * (weather.wind_strength * cfg.RAIN_WIND_SLANT)
        self.program['u_cam_center'] = (cam.x, cam.y, cam.z)
        self.program['u_wind_vel'] = (wind.x, wind.y)
        self.program['u_time'] = self.app.time
        self.program['u_alpha'] = alpha

        self.vao.render(mode=mgl.LINES, instances=cfg.RAIN_COUNT)
