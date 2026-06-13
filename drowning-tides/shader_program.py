from pyglm import glm
from settings import *


def _mix(a, b, t):
    return a + (b - a) * t


class ShaderProgram:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx

        self.sky = self.get_program('sky')
        self.water = self.get_program('water')
        self.boat = self.get_program('boat')
        self.rain = self.get_program('rain')
        self.console = self.get_program('console')
        self.post = self.get_program('post')

        self.set_uniforms_on_init()

    def set_uniforms_on_init(self):
        m_proj = glm.perspective(V_FOV, ASPECT_RATIO, NEAR, FAR)
        self.water['m_proj'].write(m_proj)
        self.boat['m_proj'].write(m_proj)
        self.rain['m_proj'].write(m_proj)

        # constant key-light direction
        self.water['sun_dir'].write(SUN_DIR)
        self.boat['sun_dir'].write(SUN_DIR)
        self.sky['sun_dir'].write(SUN_DIR)

        self.console['u_tex'] = 0
        self.post['u_scene'] = 0
        self.post['u_texel'] = (1.0 / WIN_RES.x, 1.0 / WIN_RES.y)

    def update(self):
        cam = self.app.camera
        cam_pos = cam.position
        t = self.app.time
        s = self.app.weather.storm_intensity

        # mood lighting: lerp calm <-> storm presets by storm intensity
        water_color = _mix(WATER_COLOR, WATER_COLOR_STORM, s)
        water_deep = _mix(WATER_COLOR_DEEP, WATER_COLOR_DEEP_STORM, s)
        fog_color = _mix(FOG_COLOR, FOG_COLOR_STORM, s)
        fog_near = _mix(FOG_NEAR, FOG_NEAR_STORM, s)
        fog_far = _mix(FOG_FAR, FOG_FAR_STORM, s)
        sky_top = _mix(SKY_TOP_COLOR, SKY_TOP_COLOR_STORM, s)
        sky_horizon = _mix(SKY_HORIZON_COLOR, SKY_HORIZON_COLOR_STORM, s)
        sun_strength = _mix(SUN_STRENGTH, SUN_STRENGTH_STORM, s)

        # water
        self.water['m_view'].write(cam.m_view)
        self.water['cam_pos'].write(cam_pos)
        self.water['water_color'].write(water_color)
        self.water['water_color_deep'].write(water_deep)
        self.water['fog_color'].write(fog_color)
        self.water['fog_near'] = fog_near
        self.water['fog_far'] = fog_far
        self.water['sun_strength'] = sun_strength
        self.water['storm_intensity'] = s
        self.water['time'] = t
        self.app.wave_field.write_uniforms(self.water, t)

        # boat
        self.boat['m_view'].write(cam.m_view)
        self.boat['cam_pos'].write(cam_pos)
        self.boat['fog_color'].write(fog_color)
        self.boat['fog_near'] = fog_near
        self.boat['fog_far'] = fog_far
        self.boat['sun_strength'] = sun_strength

        # sky
        inv_vp = glm.inverse(cam.m_proj * cam.m_view)
        self.sky['m_inv_view_proj'].write(inv_vp)
        self.sky['cam_pos'].write(cam_pos)
        self.sky['horizon_color'].write(sky_horizon)
        self.sky['top_color'].write(sky_top)
        self.sky['fog_color'].write(fog_color)

        # rain
        self.rain['m_view'].write(cam.m_view)

        # post
        self.post['time'] = t

    def get_program(self, shader_name):
        with open(f'shaders/{shader_name}.vert') as f:
            vertex_shader = f.read()
        with open(f'shaders/{shader_name}.frag') as f:
            fragment_shader = f.read()
        return self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
