"""A small fishing village baked onto the home island: procedural houses on the summit + a
plank dock at the waterline. Static geometry rendered with the lit `model` shader. Also
publishes `npc_spots` for the village NPCs.
"""
import math
import random

from pyglm import glm

from drowning_tides.config import settings as cfg
from drowning_tides.core.mesh import Mesh
from drowning_tides.core.meshbuilder import MeshData


class Town:
    def __init__(self, app):
        self.app = app
        self.program = app.shader_program.model
        self.home = next((i for i in app.islands.islands if i.kind == 'home'), None)
        self.npc_spots = []

        md = MeshData()
        if self.home is not None:
            self._build(md, self.home)
        self.mesh = Mesh(app.ctx, self.program, md.array(), '3f 3f 3f',
                         ('in_position', 'in_normal', 'in_color'))
        self.m_model = glm.mat4(1.0)

    def _build(self, md, home):
        rng = random.Random(1234)
        cx, cz, gy = home.position.x, home.position.z, home.land_y
        ring = home.radius * 0.32       # spread the village across the flat island
        n = cfg.TOWN_HOUSE_COUNT
        for i in range(n):
            a = (i / n) * math.tau + rng.uniform(-0.25, 0.25)
            r = ring * rng.uniform(0.6, 1.1)
            x, z = cx + math.cos(a) * r, cz + math.sin(a) * r
            w, d, h = rng.uniform(1.0, 1.6), rng.uniform(1.0, 1.6), rng.uniform(1.2, 1.8)
            md.box(x, gy + h * 0.5, z, w, h * 0.5, d, cfg.HOUSE_WALL_COLOR)
            md.gable_roof(x, gy + h, z, w * 1.12, d * 1.12, rng.uniform(0.6, 1.0),
                          cfg.HOUSE_ROOF_COLOR)
            self.npc_spots.append(glm.vec3(x + math.cos(a) * 2.4, gy, z + math.sin(a) * 2.4))

        # plank dock at the waterline, extending toward where the boat arrives (-z side)
        sx, sz = cx, cz - home.radius * 0.95
        length, width, y = 16.0, 1.6, 0.5
        md.box(sx, y, sz - length * 0.5, width, 0.12, length * 0.5, cfg.DOCK_COLOR)
        for k in range(4):
            pz = sz - (k + 0.5) * (length / 4.0)
            for px in (sx - width, sx + width):
                md.box(px, 0.0, pz, 0.12, 0.6, 0.12, cfg.DOCK_COLOR)

    def render(self):
        if self.home is None:
            return
        self.program['m_model'].write(self.m_model)
        self.mesh.render()
