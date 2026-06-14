from pathlib import Path

import numpy as np
from pyglm import glm

from drowning_tides.config import settings as cfg

SHADERS_DIR = Path(__file__).resolve().parent.parent / "shaders"


def _mix(a, b, t):
    return a + (b - a) * t


class ShaderProgram:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx

        self.sky = self.get_program('sky')
        self.water = self.get_program('water')
        self.boat = self.get_program('boat')
        self.model = self.get_program('model')
        self.rain = self.get_program('rain')
        self.console = self.get_program('console')
        self.post = self.get_program('post')
        self.godrays = self.get_program('godrays')
        self.bolt = self.get_program('bolt')

        self.set_uniforms_on_init()

    def set_uniforms_on_init(self):
        m_proj = glm.perspective(cfg.V_FOV, cfg.ASPECT_RATIO, cfg.NEAR, cfg.FAR)
        self.water['m_proj'].write(m_proj)
        self.boat['m_proj'].write(m_proj)
        self.model['m_proj'].write(m_proj)
        self.rain['m_proj'].write(m_proj)
        self.bolt['m_proj'].write(m_proj)
        self.bolt['u_color'].write(cfg.BOLT_COLOR)

        # god rays (constants; sun_uv + intensity written per frame by the scene)
        self.godrays['u_scene'] = 0
        self.godrays['u_samples'] = cfg.GODRAY_SAMPLES
        self.godrays['u_decay'] = cfg.GODRAY_DECAY
        self.godrays['u_weight'] = cfg.GODRAY_WEIGHT

        # light direction + sun/moon discs now move with the day cycle (written per frame)

        self.console['u_tex'] = 0
        self.post['u_scene'] = 0
        self.post['u_bloom'] = 1
        self.post['u_godrays'] = 2
        self.post['u_bloom_intensity'] = cfg.BLOOM_INTENSITY
        self.post['u_texel'] = (1.0 / cfg.WIN_RES.x, 1.0 / cfg.WIN_RES.y)

        # sky: cloud + aurora constants (set once)
        self.sky['u_cloud_scale'] = cfg.CLOUD_SCALE
        self.sky['u_cloud_speed'] = cfg.CLOUD_SPEED
        self.sky['u_cloud_lit'].write(cfg.CLOUD_COLOR)
        self.sky['u_cloud_dark'].write(cfg.CLOUD_COLOR_DARK)
        self.sky['u_cloud_storm'].write(cfg.CLOUD_COLOR_STORM)
        self.sky['u_aurora'] = cfg.AURORA_STRENGTH
        self.sky['u_aurora_a'].write(cfg.AURORA_COLOR_A)
        self.sky['u_aurora_b'].write(cfg.AURORA_COLOR_B)

        # water: scene/depth samplers + realism constants (set once)
        self.water['u_scene'] = 0
        self.water['u_depth'] = 1
        self.water['u_resolution'] = (cfg.WIN_RES.x, cfg.WIN_RES.y)
        self.water['u_near'] = cfg.NEAR
        self.water['u_far'] = cfg.FAR
        self.water['u_refraction'] = cfg.WATER_REFRACTION
        self.water['u_clarity'] = cfg.WATER_CLARITY
        self.water['u_absorb'].write(cfg.WATER_ABSORB)
        self.water['u_detail'] = cfg.WATER_DETAIL
        self.water['u_detail_scale'] = cfg.WATER_DETAIL_SCALE
        self.water['u_sun_reflect_shininess'] = cfg.WATER_SUN_REFLECT_SHININESS

    def set_shallows(self, islands):
        """Upload the (static) island disc data the water shader uses for shallows tint."""
        cap = cfg.MAX_SHALLOW_ISLANDS
        n = min(len(islands), cap)
        xz = np.zeros((cap, 2), dtype='f4')
        rad = np.zeros(cap, dtype='f4')
        for i in range(n):
            xz[i] = (islands[i].position.x, islands[i].position.z)
            rad[i] = islands[i].radius
        self.water['u_island_count'] = n
        self.water['u_island_xz'].write(xz.tobytes())
        self.water['u_island_radius'].write(rad.tobytes())
        self.water['u_shallow_color'].write(cfg.SHALLOW_COLOR)
        self.water['u_shallow_band'] = cfg.SHALLOW_BAND

    def update(self):
        cam = self.app.camera
        cam_pos = cam.position
        t = self.app.time
        weather = self.app.weather
        s = weather.storm_intensity
        fog_i = weather.fog_intensity
        lightning = weather.lightning
        day = self.app.daycycle
        pal = day.palette

        # base mood comes from the time of day; storms lerp it toward the storm presets...
        water_color = _mix(pal.water_color, cfg.WATER_COLOR_STORM, s)
        water_deep = _mix(pal.water_color_deep, cfg.WATER_COLOR_DEEP_STORM, s)
        sky_top = _mix(pal.sky_top, cfg.SKY_TOP_COLOR_STORM, s)
        sky_horizon = _mix(pal.sky_horizon, cfg.SKY_HORIZON_COLOR_STORM, s)
        sun_strength = _mix(pal.sun_strength, cfg.SUN_STRENGTH_STORM, s)

        # ...then fog banks (independent of storms) close the horizon further
        fog_color = _mix(pal.fog_color, cfg.FOG_COLOR_STORM, s)
        fog_color = _mix(fog_color, cfg.FOG_TINT, fog_i)
        fog_near = _mix(_mix(pal.fog_near, cfg.FOG_NEAR_STORM, s), cfg.FOG_DENSE_NEAR, fog_i)
        fog_far = _mix(_mix(pal.fog_far, cfg.FOG_FAR_STORM, s), cfg.FOG_DENSE_FAR, fog_i)

        light_dir = day.light_dir
        light_color = day.light_color
        star_alpha = day.star_alpha * (1.0 - 0.7 * s) * (1.0 - 0.6 * fog_i)

        # water
        self.water['m_view'].write(cam.m_view)
        self.water['cam_pos'].write(cam_pos)
        self.water['light_dir'].write(light_dir)
        self.water['light_color'].write(light_color)
        self.water['sky_color'].write(sky_horizon)
        self.water['sky_top'].write(sky_top)
        self.water['water_color'].write(water_color)
        self.water['water_color_deep'].write(water_deep)
        self.water['fog_color'].write(fog_color)
        self.water['fog_near'] = fog_near
        self.water['fog_far'] = fog_far
        self.water['sun_strength'] = sun_strength
        self.water['storm_intensity'] = s
        self.water['u_lightning'] = lightning
        self.water['time'] = t
        self.app.wave_field.write_uniforms(self.water, t)

        # boat + loaded models share the moving key light and mood fog
        for prog in (self.boat, self.model):
            prog['m_view'].write(cam.m_view)
            prog['cam_pos'].write(cam_pos)
            prog['sun_dir'].write(light_dir)
            prog['fog_color'].write(fog_color)
            prog['fog_near'] = fog_near
            prog['fog_far'] = fog_far
            prog['sun_strength'] = sun_strength
            prog['u_lightning'] = lightning

        # sky
        inv_vp = glm.inverse(cam.m_proj * cam.m_view)
        self.sky['m_inv_view_proj'].write(inv_vp)
        self.sky['cam_pos'].write(cam_pos)
        self.sky['horizon_color'].write(sky_horizon)
        self.sky['top_color'].write(sky_top)
        self.sky['fog_color'].write(fog_color)
        self.sky['sun_dir'].write(day.sun_dir)
        self.sky['moon_dir'].write(day.moon_dir)
        self.sky['sun_color'].write(cfg.SUN_COLOR)
        self.sky['moon_color'].write(cfg.MOON_COLOR)
        self.sky['star_alpha'] = star_alpha
        self.sky['u_time'] = t
        self.sky['u_wind_dir'] = (weather.wind_dir.x, weather.wind_dir.y)
        self.sky['u_cloud_cover'] = weather.cloud_cover
        self.sky['u_storm'] = s
        self.sky['u_lightning'] = lightning

        # rain
        self.rain['m_view'].write(cam.m_view)

        # post
        self.post['time'] = t

    def get_program(self, shader_name):
        with open(SHADERS_DIR / f'{shader_name}.vert') as f:
            vertex_shader = f.read()
        with open(SHADERS_DIR / f'{shader_name}.frag') as f:
            fragment_shader = f.read()
        return self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
