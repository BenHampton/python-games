import math

import numpy as np
import pygame as pg
from pyglm import glm

from drowning_tides.config import settings as cfg
from drowning_tides.core.mesh import Mesh
from drowning_tides.core.model import MODELS_DIR, load_vertices


class Boat:
    """Low-poly fishing boat + physics-driven movement.

    Local space: bow points toward +Z. Heading yaw=0 => forward = +Z. Geometry is an
    authored glTF model when cfg.BOAT_MODEL points at one (e.g. a CC0 boat dropped into
    assets/models/), otherwise the built-in procedural hull.
    """

    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx

        # geometry: authored model if configured + present, else the procedural hull
        model_path = (MODELS_DIR / cfg.BOAT_MODEL) if cfg.BOAT_MODEL else None
        self.using_model = bool(model_path and model_path.exists())
        if self.using_model:
            self.program = app.shader_program.model
            verts = load_vertices(model_path)
            self.draw_scale = cfg.BOAT_MODEL_SCALE
            self.yaw_offset = cfg.BOAT_MODEL_YAW
            self.y_offset = cfg.BOAT_MODEL_Y_OFFSET
        else:
            self.program = app.shader_program.boat
            verts = self._build()
            self.draw_scale = cfg.BOAT_SCALE
            self.yaw_offset = 0.0
            self.y_offset = 0.0

        # physics state
        self.position = glm.vec3(cfg.BOAT_START_POS)
        self.yaw = cfg.BOAT_START_YAW   # radians, heading about +Y (moored alongside the pier)
        self.speed = 0.0        # signed scalar along forward
        self.pitch = 0.0        # set by wave sampling (stub for now)
        self.roll = 0.0
        self.docked_pos = None  # glm.vec2(x, z) anchor while disembarked; None when sailing

        self.mesh = Mesh(
            self.ctx, self.program, verts, '3f 3f 3f',
            ('in_position', 'in_normal', 'in_color'),
        )
        self.m_model = glm.mat4(1.0)

    # ------------------------------------------------------------------ geometry
    def _build(self):
        verts = []  # flat list of (pos, normal, color)

        def add_tri(p0, p1, p2, color):
            n = glm.normalize(glm.cross(glm.vec3(*p1) - glm.vec3(*p0),
                                        glm.vec3(*p2) - glm.vec3(*p0)))
            nrm = (n.x, n.y, n.z)
            for p in (p0, p1, p2):
                verts.append((p, nrm, color))

        def add_quad(p0, p1, p2, p3, color):
            add_tri(p0, p1, p2, color)
            add_tri(p0, p2, p3, color)

        hull_color = (0.09, 0.12, 0.14)
        deck_color = (0.20, 0.16, 0.12)
        cabin_color = (0.24, 0.22, 0.20)
        cabin_roof = (0.30, 0.16, 0.13)

        # cross-section stations along Z: (z, half_width, keel_depth, deck_y)
        stations = [
            (-2.0, 1.00, 0.55, 0.35),   # transom / stern
            (-1.0, 1.10, 0.62, 0.35),
            (0.5, 1.05, 0.62, 0.35),
            (1.8, 0.70, 0.50, 0.38),
            (3.0, 0.06, 0.16, 0.46),    # bow (nearly closed -> sharp prow)
        ]

        def section_points(z, w, d, dy):
            # port gunwale -> port chine -> keel -> starboard chine -> starboard gunwale
            return [
                (-w, dy, z),
                (-w * 0.6, dy - d * 0.55, z),
                (0.0, dy - d, z),
                (w * 0.6, dy - d * 0.55, z),
                (w, dy, z),
            ]

        secs = [section_points(*s) for s in stations]

        # loft the hull sides + bottom between adjacent stations
        for a, b in zip(secs[:-1], secs[1:], strict=True):
            for k in range(4):
                add_quad(a[k], a[k + 1], b[k + 1], b[k], hull_color)

        # flat deck following the gunwale outline (top quads between port/starboard)
        for a, b in zip(secs[:-1], secs[1:], strict=True):
            add_quad(a[0], b[0], b[4], a[4], deck_color)

        # transom cap (close the stern): fan from keel point of the stern section
        st = secs[0]
        keel = st[2]
        ring = [st[0], st[1], st[2], st[3], st[4]]  # bottom edge across stern
        # bottom triangles of the stern face
        add_tri(ring[0], ring[1], keel, hull_color)
        add_tri(ring[1], ring[2], keel, hull_color)
        add_tri(ring[2], ring[3], keel, hull_color)
        add_tri(ring[3], ring[4], keel, hull_color)
        # upper transom rectangle (between gunwales, above keel level)
        add_quad(st[0], st[4],
                 (st[4][0], st[4][1], st[4][2]), (st[0][0], st[0][1], st[0][2]),
                 hull_color)  # degenerate-safe; deck already covers top edge

        # --- cabin / wheelhouse box near the stern for a fishing-boat silhouette ---
        cx, cz0, cz1 = 0.0, -1.6, -0.2
        cw, cy0, cy1 = 0.6, 0.35, 1.15
        # corners
        v000 = (cx - cw, cy0, cz0)
        v100 = (cx + cw, cy0, cz0)
        v110 = (cx + cw, cy1, cz0)
        v010 = (cx - cw, cy1, cz0)
        v001 = (cx - cw, cy0, cz1)
        v101 = (cx + cw, cy0, cz1)
        v111 = (cx + cw, cy1, cz1)
        v011 = (cx - cw, cy1, cz1)
        add_quad(v001, v101, v111, v011, cabin_color)   # front (+Z)
        add_quad(v100, v000, v010, v110, cabin_color)   # back (-Z)
        add_quad(v000, v001, v011, v010, cabin_color)   # left (-X)
        add_quad(v101, v100, v110, v111, cabin_color)   # right (+X)
        add_quad(v010, v011, v111, v110, cabin_roof)    # roof

        data = []
        for p, n, c in verts:
            data.extend([*p, *n, *c])
        return np.array(data, dtype='f4')

    # ------------------------------------------------------------------- physics
    @property
    def forward(self):
        return glm.vec3(math.sin(self.yaw), 0.0, math.cos(self.yaw))

    def sample_surface(self, x, z):
        """Return (height, normal) of the wave surface at world (x, z), evaluated
        with the same Gerstner field the water shader displaces.
        """
        return self.app.wave_field.sample(x, z, self.app.time)

    def update(self, dt):
        if self.app.game_state.is_helm():
            # take helm input only while the console isn't capturing keystrokes
            controls = not self.app.console.active
            keys = pg.key.get_pressed()

            if controls and keys[cfg.KEYS['THROTTLE_UP']]:
                self.speed += cfg.BOAT_ACCEL * dt
            if controls and keys[cfg.KEYS['THROTTLE_DOWN']]:
                self.speed -= cfg.BOAT_REVERSE_ACCEL * dt

            # water drag (exponential decay toward zero when coasting)
            self.speed *= math.exp(-cfg.WATER_DRAG * dt)
            self.speed = max(-cfg.BOAT_MAX_REVERSE, min(cfg.BOAT_MAX_SPEED, self.speed))

            # steering: authority grows with speed -> wide turns fast, sluggish near stop
            turn = 0.0
            if controls and keys[cfg.KEYS['TURN_LEFT']]:
                turn += 1.0
            if controls and keys[cfg.KEYS['TURN_RIGHT']]:
                turn -= 1.0
            authority = min(1.0, abs(self.speed) / (cfg.BOAT_MAX_SPEED * cfg.TURN_SPEED_FACTOR))
            helm_sign = 1.0 if self.speed >= 0.0 else -1.0   # reverse helm when backing up
            self.yaw += turn * cfg.BOAT_TURN_RATE * authority * helm_sign * dt

            # integrate helm motion, then add the wind-driven current (storm push)
            self.position += self.forward * (self.speed * dt)
            self.position += self.app.weather.current_vector() * dt

            # keep off the land: push out of island discs and bleed speed on impact
            x, z, hit = self.app.islands.collide(
                self.position.x, self.position.z, cfg.BOAT_COLLISION_RADIUS
            )
            town = getattr(self.app, 'town', None)
            if town is not None:
                x, z, dock_hit = town.collide_boat(x, z, cfg.BOAT_COLLISION_RADIUS)
                hit = hit or dock_hit
            self.position.x, self.position.z = x, z
            if hit:
                self.speed *= cfg.BOAT_COLLISION_BLEED
        else:
            # docked / disembarked: anchored to the docked spot — no drift, just bobs
            self.speed = 0.0
            if self.docked_pos is not None:
                self.position.x = self.docked_pos.x
                self.position.z = self.docked_pos.y

        # ride the waves: sit at the surface height and tilt toward its slope
        h, normal = self.sample_surface(self.position.x, self.position.z)
        self.position.y = h

        fwd = self.forward
        right = glm.vec3(fwd.z, 0.0, -fwd.x)
        target_pitch = -math.asin(max(-1.0, min(1.0, glm.dot(normal, fwd))))
        target_roll = math.asin(max(-1.0, min(1.0, glm.dot(normal, right))))
        # clamp so the boat is rocked but can never flip
        target_pitch = max(-cfg.BOAT_MAX_TILT, min(cfg.BOAT_MAX_TILT, target_pitch))
        target_roll = max(-cfg.BOAT_MAX_TILT, min(cfg.BOAT_MAX_TILT, target_roll))
        # ease toward the target tilt for smooth rocking
        a = 1.0 - math.exp(-cfg.BOAT_TILT_EASE * dt) if dt > 0.0 else 1.0
        self.pitch += (target_pitch - self.pitch) * a
        self.roll += (target_roll - self.roll) * a

        self._update_model()

    def _update_model(self):
        m = glm.translate(glm.mat4(1.0), self.position + glm.vec3(0.0, self.y_offset, 0.0))
        m = glm.rotate(m, self.yaw + self.yaw_offset, glm.vec3(0, 1, 0))
        m = glm.rotate(m, self.pitch, glm.vec3(1, 0, 0))
        m = glm.rotate(m, self.roll, glm.vec3(0, 0, 1))
        m = glm.scale(m, glm.vec3(self.draw_scale))
        self.m_model = m

    def render(self):
        self.program['m_model'].write(self.m_model)
        self.mesh.render()
