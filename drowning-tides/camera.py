import math
from pyglm import glm
from settings import *

FOLLOW = 'follow'
FIRST_PERSON = 'first_person'


class Camera:
    """Third-person follow camera now; a first-person on-deck mode is stubbed for
    the future 'toon walking the deck' feature.
    """

    def __init__(self, app, mode=FOLLOW):
        self.app = app
        self.mode = mode
        self.up = glm.vec3(0, 1, 0)

        self.m_proj = glm.perspective(V_FOV, ASPECT_RATIO, NEAR, FAR)
        self.m_view = glm.mat4(1.0)

        boat = app.boat
        # start already positioned behind the boat (no opening lurch)
        self.position = boat.position - boat.forward * CAM_DISTANCE + self.up * CAM_HEIGHT
        self.update(0.0)

    def update(self, dt):
        if self.mode == FOLLOW:
            self._update_follow(dt)
        else:
            self._update_first_person(dt)
        self.m_view = glm.lookAt(self.position, self._look_target, self.up)

    def _update_follow(self, dt):
        boat = self.app.boat
        target = boat.position
        desired = target - boat.forward * CAM_DISTANCE + self.up * CAM_HEIGHT
        # frame-rate independent smoothing toward the desired pose
        alpha = 1.0 - math.exp(-CAM_LERP * dt) if dt > 0.0 else 1.0
        self.position = glm.mix(self.position, desired, alpha)
        self._look_target = target + glm.vec3(0, CAM_LOOK_HEIGHT, 0)

    def _update_first_person(self, dt):
        # TODO: lock to a deck anchor + mouse-look when the on-deck mode lands
        boat = self.app.boat
        self.position = boat.position + glm.vec3(0, 1.4, 0)
        self._look_target = self.position + boat.forward
