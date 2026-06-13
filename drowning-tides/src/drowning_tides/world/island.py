"""Islands: low-poly glTF models placed in the world, with simple disc collision.

Geometry is authored as a glTF model (see `tools/gen_island.py`) and loaded through the
shared `core/model.py::Model` so it renders with the lit `model` shader. Collision is a
flat cylinder per island — cheap and enough to stop the boat sailing through land.
"""
import math

from pyglm import glm

from drowning_tides.config import settings as cfg
from drowning_tides.core.model import MODELS_DIR, Model


class Island:
    def __init__(self, app, position, scale, yaw, radius):
        self.position = glm.vec3(*position)
        self.radius = radius
        self.model = Model(
            app.ctx, app.shader_program.model, MODELS_DIR / cfg.ISLAND_MODEL,
            position=position, scale=scale, yaw=yaw,
        )

    def render(self):
        self.model.render()


def load_islands(app):
    return [
        Island(app, i['pos'], i['scale'], i['yaw'], i['radius'])
        for i in cfg.ISLANDS
    ]


def resolve_collision(x, z, islands, boat_radius):
    """Push (x, z) out of any island disc. Returns (x, z, hit)."""
    hit = False
    for isl in islands:
        dx = x - isl.position.x
        dz = z - isl.position.z
        d = math.hypot(dx, dz)
        min_d = isl.radius + boat_radius
        if d < min_d:
            hit = True
            if d > 1e-5:
                x = isl.position.x + dx / d * min_d
                z = isl.position.z + dz / d * min_d
            else:
                x = isl.position.x + min_d
    return x, z, hit
