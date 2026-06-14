"""NPC boats: other vessels that patrol the sea on slow circular paths, bobbing on the
waves. Reuses the player's boat glTF model (no new assets).
"""
import math

from pyglm import glm

from drowning_tides.config import settings as cfg
from drowning_tides.core.model import MODELS_DIR, Model

# (centre x, z, patrol radius, start angle)
_PATROLS = [
    (0.0, -90.0, 70.0, 0.0),
    (340.0, -360.0, 95.0, 2.1),
    (-150.0, 160.0, 75.0, 4.2),
    (520.0, 40.0, 80.0, 1.0),
]


class NpcBoat:
    def __init__(self, app, cx, cz, radius, angle):
        self.app = app
        self.cx, self.cz, self.radius, self.angle = cx, cz, radius, angle
        self.model = Model(app.ctx, app.shader_program.model, MODELS_DIR / cfg.BOAT_MODEL,
                           scale=cfg.BOAT_MODEL_SCALE)

    def update(self, dt):
        self.angle += (cfg.NPC_BOAT_SPEED / max(self.radius, 1.0)) * dt
        x = self.cx + math.cos(self.angle) * self.radius
        z = self.cz + math.sin(self.angle) * self.radius
        y = self.app.wave_field.sample(x, z, self.app.time)[0] + cfg.BOAT_MODEL_Y_OFFSET
        yaw = self.angle + math.pi * 0.5 + cfg.BOAT_MODEL_YAW
        m = glm.translate(glm.mat4(1.0), glm.vec3(x, y, z))
        m = glm.rotate(m, yaw, glm.vec3(0, 1, 0))
        m = glm.scale(m, glm.vec3(cfg.BOAT_MODEL_SCALE))
        self.model.m_model = m

    def render(self):
        self.model.render()


class NpcBoats:
    def __init__(self, app):
        self.boats = []
        have_model = cfg.BOAT_MODEL and (MODELS_DIR / cfg.BOAT_MODEL).exists()
        if have_model:
            for cx, cz, r, a in _PATROLS[:cfg.NPC_BOAT_COUNT]:
                self.boats.append(NpcBoat(app, cx, cz, r, a))

    def update(self, dt):
        for b in self.boats:
            b.update(dt)

    def render(self):
        for b in self.boats:
            b.render()
