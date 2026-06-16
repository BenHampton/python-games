"""Ambient gulls: a few low-poly birds to make the world feel alive. Some perch on the
dock / shore / water and take off when the player (or boat) gets close; a couple wheel high
overhead as pure ambience. Procedural mesh (no assets), drawn per-instance like the village
NPCs. The flee/flight maths are pure helpers so they stay unit-testable without a GL context.
"""
import math
import random

from pyglm import glm

from drowning_tides.config import settings as cfg
from drowning_tides.core.mesh import Mesh
from drowning_tides.core.meshbuilder import MeshData

PERCHED, FLYING, SOARING = 'perched', 'flying', 'soaring'


# ------------------------------------------------------------------ pure helpers (tested)
def should_flee(dist, flee_range):
    """True when a threat is close enough to spook a perched bird."""
    return dist < flee_range


def flee_velocity(bird_xz, threat_xz, speed):
    """Horizontal escape velocity: away from the threat at `speed` (arbitrary dir if on top)."""
    away = bird_xz - threat_xz
    if glm.length(away) < 1e-6:
        away = glm.vec2(1.0, 0.0)
    return glm.normalize(away) * speed


def climb_step(y, target_y, rate, dt):
    """Ease an altitude toward `target_y` (exponential approach), framerate-independent."""
    return y + (target_y - y) * (1.0 - math.exp(-rate * dt))


# ----------------------------------------------------------------------------- gull mesh
def _gull_meshes(ctx, program):
    """Build the three shared meshes (body, right wing, left wing). Wings are single triangles
    hinged on the body centreline (built explicitly per side so normals stay correct) and flap by
    rotating about the forward (+X) axis."""
    body = MeshData()
    body.box(0.0, 0.0, 0.0, 0.42, 0.16, 0.18, cfg.BIRD_BODY_COLOR)   # stubby body
    body.box(0.5, 0.04, 0.0, 0.18, 0.07, 0.07, cfg.BIRD_TIP_COLOR)   # head/beak nub

    span, chord, lift = 1.0, 0.30, 0.05
    right = MeshData()
    right.tri((chord, 0.0, 0.10), (-chord, 0.0, 0.10), (0.0, lift, span), cfg.BIRD_WING_COLOR)
    right.tri((0.0, lift, span * 0.7), (-chord * 0.6, 0.0, span), (chord * 0.6, 0.0, span),
              cfg.BIRD_TIP_COLOR)                                    # darker wingtip
    left = MeshData()
    left.tri((-chord, 0.0, -0.10), (chord, 0.0, -0.10), (0.0, lift, -span), cfg.BIRD_WING_COLOR)
    left.tri((-chord * 0.6, 0.0, -span), (0.0, lift, -span * 0.7), (chord * 0.6, 0.0, -span),
             cfg.BIRD_TIP_COLOR)

    def mk(md):
        return Mesh(ctx, program, md.array(), '3f 3f 3f',
                    ('in_position', 'in_normal', 'in_color'))
    return mk(body), mk(right), mk(left)


class Bird:
    def __init__(self, app, mode):
        self.app = app
        self.pos = glm.vec3(0.0)
        self.vel = glm.vec2(0.0)        # horizontal velocity (xz)
        self.heading = random.uniform(0.0, math.tau)
        self.bank = 0.0
        self.phase = random.uniform(0.0, math.tau)
        self.flap = 0.0
        self.activity = 0.0             # 0 perched/gliding .. 1 flapping hard
        self.flee_timer = 0.0
        self.perch_kind = 'water'
        self.perch_y = 0.0
        # soarers circle high forever; perchers cycle perch -> flee -> respawn
        if mode == SOARING:
            self.mode = SOARING
            self.cx, self.cz = cfg.SHELTER_CENTER.x, cfg.SHELTER_CENTER.y
            self.radius = random.uniform(*cfg.BIRD_SOAR_RADIUS)
            self.angle = random.uniform(0.0, math.tau)
            self.alt = cfg.BIRD_CRUISE_Y + random.uniform(-8.0, 12.0)
        else:
            self.mode = PERCHED
            self._respawn()

    # ----------------------------------------------------------------- perch placement
    def _random_perch(self):
        """Pick a fresh perch: on the water, on a dock deck, or on the home-island shore."""
        home = getattr(self.app.town, 'home', None)
        decks = getattr(self.app.town, 'flat_decks', [])
        choices = ['water']
        if home is not None:
            choices.append('land')
        if decks:
            choices.append('dock')
        kind = random.choice(choices)
        cx, cz = cfg.SHELTER_CENTER.x, cfg.SHELTER_CENTER.y
        if kind == 'dock':
            x0, z0, x1, z1, dy = random.choice(decks)
            return 'dock', random.uniform(x0, x1), random.uniform(z0, z1), dy
        if kind == 'land':
            r = home.radius * cfg.HOME_WALK_FRAC * random.uniform(0.15, 0.85)
            a = random.uniform(0.0, math.tau)
            x, z = cx + math.cos(a) * r, cz + math.sin(a) * r
            return 'land', x, z, home.ground_y(x, z)
        # water: an annulus of open sea around the harbour (outside the island)
        r = random.uniform(*cfg.BIRD_WATER_RADIUS)
        a = random.uniform(0.0, math.tau)
        return 'water', cx + math.cos(a) * r, cz + math.sin(a) * r, 0.0

    def _respawn(self):
        self.perch_kind, x, z, self.perch_y = self._random_perch()
        self.pos = glm.vec3(x, self.perch_y, z)
        self.vel = glm.vec2(0.0)
        self.activity = 0.0
        self.heading = random.uniform(0.0, math.tau)
        self.mode = PERCHED

    def _perch_height(self, t):
        if self.perch_kind == 'water':
            return self.app.wave_field.sample(self.pos.x, self.pos.z, t)[0]
        return self.perch_y

    def _spook(self, threat_xz):
        self.mode = FLYING
        self.vel = flee_velocity(glm.vec2(self.pos.x, self.pos.z), threat_xz, cfg.BIRD_FLEE_SPEED)
        self.heading = math.atan2(self.vel.x, self.vel.y)
        self.activity = 1.0
        self.flee_timer = cfg.BIRD_FLY_TIME

    # ------------------------------------------------------------------------- per-frame
    def update(self, dt, t, threat_xz):
        if self.mode == SOARING:
            self.angle += cfg.BIRD_SOAR_SPEED / max(self.radius, 1.0) * dt
            self.pos = glm.vec3(self.cx + math.cos(self.angle) * self.radius,
                                self.alt + math.sin(t * 0.3 + self.phase) * 3.0,
                                self.cz + math.sin(self.angle) * self.radius)
            self.heading = self.angle + math.pi * 0.5
            self.bank = 0.35
            self.activity = 0.25
        elif self.mode == PERCHED:
            self.pos.y = self._perch_height(t)
            self.activity = 0.0
            self.bank = 0.0
            d = glm.length(glm.vec2(self.pos.x, self.pos.z) - threat_xz)
            if should_flee(d, cfg.BIRD_FLEE_RANGE):
                self._spook(threat_xz)
        else:  # FLYING: climb out, ease to a glide, then respawn elsewhere
            self.pos.x += self.vel.x * dt
            self.pos.z += self.vel.y * dt
            self.pos.y = climb_step(self.pos.y, cfg.BIRD_CRUISE_Y, cfg.BIRD_CLIMB_RATE, dt)
            self.heading = math.atan2(self.vel.x, self.vel.y)
            self.bank = 0.25
            self.activity = max(0.2, self.activity - dt * 0.4)   # flap hard -> glide
            self.flee_timer -= dt
            if self.flee_timer <= 0.0:
                self._respawn()

        # wing flap: amplitude rides on activity; folded & still when perched
        rate = cfg.BIRD_FLAP_RATE * (0.4 + self.activity)
        self.flap = cfg.BIRD_FLAP_AMPL * self.activity * math.sin(t * rate + self.phase)

    def render(self, program, body, wing_r, wing_l):
        world = glm.translate(glm.mat4(1.0), self.pos)
        world = glm.rotate(world, self.heading, glm.vec3(0, 1, 0))
        world = glm.rotate(world, self.bank, glm.vec3(1, 0, 0))
        world = glm.scale(world, glm.vec3(cfg.BIRD_SCALE))
        program['m_model'].write(world)
        body.render()
        program['m_model'].write(world * glm.rotate(glm.mat4(1.0), self.flap, glm.vec3(1, 0, 0)))
        wing_r.render()
        program['m_model'].write(world * glm.rotate(glm.mat4(1.0), -self.flap, glm.vec3(1, 0, 0)))
        wing_l.render()


class Birds:
    """A handful of gulls: `BIRD_PERCH_COUNT` perchers that flee on approach + `BIRD_SOAR_COUNT`
    high soarers. Built/updated/rendered like NpcCrowd / NpcBoats."""

    def __init__(self, app):
        self.app = app
        self.program = app.shader_program.model
        self.body, self.wing_r, self.wing_l = _gull_meshes(app.ctx, self.program)
        self.birds = [Bird(app, PERCHED) for _ in range(cfg.BIRD_PERCH_COUNT)]
        self.birds += [Bird(app, SOARING) for _ in range(cfg.BIRD_SOAR_COUNT)]

    def _threat_xz(self):
        """The thing birds flee from: the boat at the helm, else the on-foot player."""
        e = self.app.boat if self.app.game_state.is_helm() else self.app.player
        return glm.vec2(e.position.x, e.position.z)

    def update(self, dt):
        t = self.app.time
        threat = self._threat_xz()
        for b in self.birds:
            b.update(dt, t, threat)

    def render(self):
        for b in self.birds:
            b.render(self.program, self.body, self.wing_r, self.wing_l)
