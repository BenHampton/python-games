import math

from pyglm import glm

from drowning_tides.config import settings as cfg

FOLLOW = 'follow'
FIRST_PERSON = 'first_person'


class Camera:
    """Third-person orbit camera driven by the mouse. Yaw/pitch are world-space so the
    framed angle holds while the boat turns; scroll zooms the orbit distance. A
    first-person on-deck mode is stubbed for the future 'toon walking the deck' feature.
    """

    def __init__(self, app, mode=FOLLOW):
        self.app = app
        self.mode = mode
        self.up = glm.vec3(0, 1, 0)

        self.m_proj = glm.perspective(cfg.V_FOV, cfg.ASPECT_RATIO, cfg.NEAR, cfg.FAR)
        self.m_view = glm.mat4(1.0)

        # orbit state (world-space): start framed behind the boat
        self.orbit_yaw = app.boat.yaw + math.pi
        self.orbit_pitch = cfg.CAM_PITCH_START
        self.distance = cfg.CAM_DISTANCE

        self.position = self._desired()
        self.update(0.0)

    # ------------------------------------------------------------------- mouse input
    def add_look(self, dx, dy):
        self.orbit_yaw += dx * cfg.MOUSE_SENSITIVITY
        sign = 1.0 if cfg.INVERT_Y else -1.0
        self.orbit_pitch += sign * dy * cfg.MOUSE_SENSITIVITY
        if self.mode == FIRST_PERSON:
            lo, hi = cfg.FP_PITCH_MIN, cfg.FP_PITCH_MAX
        else:
            lo, hi = cfg.CAM_PITCH_MIN, cfg.CAM_PITCH_MAX
        self.orbit_pitch = max(lo, min(hi, self.orbit_pitch))

    def zoom(self, steps):
        self.distance -= steps * cfg.CAM_ZOOM_STEP
        self.distance = max(cfg.CAM_DISTANCE_MIN, min(cfg.CAM_DISTANCE_MAX, self.distance))

    # ----------------------------------------------------------------------- update
    def update(self, dt):
        if self.mode == FOLLOW:
            self._update_follow(dt)
        else:
            self._update_first_person(dt)
        self.m_view = glm.lookAt(self.position, self._look_target, self.up)

    def _pivot(self):
        return self.app.boat.position + glm.vec3(0, cfg.CAM_LOOK_HEIGHT, 0)

    def _desired(self):
        cp = math.cos(self.orbit_pitch)
        offset = glm.vec3(
            cp * math.sin(self.orbit_yaw),
            math.sin(self.orbit_pitch),
            cp * math.cos(self.orbit_yaw),
        ) * self.distance
        return self._pivot() + offset

    def _update_follow(self, dt):
        desired = self._desired()
        # frame-rate independent smoothing toward the desired pose
        alpha = 1.0 - math.exp(-cfg.CAM_LERP * dt) if dt > 0.0 else 1.0
        self.position = glm.mix(self.position, desired, alpha)
        self._look_target = self._pivot()

    def _update_first_person(self, dt):
        # eye at the on-foot player; look from the mouse-driven yaw/pitch
        self.position = self.app.player.position + glm.vec3(0.0, cfg.PLAYER_EYE_HEIGHT, 0.0)
        cp = math.cos(self.orbit_pitch)
        look = glm.vec3(
            math.sin(self.orbit_yaw) * cp,
            math.sin(self.orbit_pitch),
            math.cos(self.orbit_yaw) * cp,
        )
        self._look_target = self.position + look
