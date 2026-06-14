"""Village NPCs: simple low-poly figures that idle on the home island and speak
theme-flavoured folklore when the player talks to them (F, on foot, in range).
"""
import math
import random

from pyglm import glm

from drowning_tides.config import settings as cfg
from drowning_tides.core.mesh import Mesh
from drowning_tides.core.meshbuilder import MeshData

LINES = [
    "Don't sail past the lighthouse after dark. It moves.",
    "Found a boat adrift last week. Engine warm, no soul aboard.",
    "The sea's been singing again. You'll hear it out in the deep.",
    "You came back. They always come back.",
    "Salt's heavy in the wind tonight. Keep your lantern lit.",
    "Some catches shouldn't be eaten. You'll know them when you pull them up.",
    "The water remembers your name, friend. I'd not answer it.",
]


class Npc:
    def __init__(self, ctx, program, position):
        md = MeshData()
        md.box(0.0, 0.55, 0.0, 0.22, 0.55, 0.16, cfg.NPC_BODY_COLOR)
        md.box(0.0, 1.28, 0.0, 0.18, 0.18, 0.18, cfg.NPC_HEAD_COLOR)
        self.mesh = Mesh(ctx, program, md.array(), '3f 3f 3f',
                         ('in_position', 'in_normal', 'in_color'))
        self.position = position
        self.phase = random.uniform(0.0, math.tau)

    def render(self, program, t):
        m = glm.translate(glm.mat4(1.0), self.position)
        m = glm.rotate(m, 0.3 * math.sin(t * 0.6 + self.phase), glm.vec3(0, 1, 0))  # idle sway
        program['m_model'].write(m)
        self.mesh.render()


class NpcCrowd:
    def __init__(self, app):
        self.app = app
        self.program = app.shader_program.model
        spots = app.town.npc_spots[:cfg.NPC_COUNT]
        self.npcs = [Npc(app.ctx, self.program, s) for s in spots]
        self.rng = random.Random()

    def render(self):
        t = self.app.time
        for npc in self.npcs:
            npc.render(self.program, t)

    def try_talk(self, pos):
        """Return a line from the nearest NPC within interact range, else None."""
        for npc in self.npcs:
            if glm.distance(pos, npc.position) < cfg.NPC_INTERACT_RANGE:
                return self.rng.choice(LINES)
        return None
