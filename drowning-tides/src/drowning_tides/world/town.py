"""A small fishing village on the home island: procedural houses + a plank dock + lamp posts,
plus CC0 Kenney props (crates, barrels, a flag, a watchtower landmark) and Nature-Kit fences
lining the path. Props sit on the island's ramped ground via Island.ground_y so they follow the
beach slope.
"""
import math
import random

from pyglm import glm

from drowning_tides.config import settings as cfg
from drowning_tides.core.mesh import Mesh
from drowning_tides.core.meshbuilder import MeshData
from drowning_tides.core.model import MODELS_DIR, Model

PROPS_DIR = MODELS_DIR / "props"
NATURE_DIR = MODELS_DIR / "nature"

DECK_Y = 0.6                       # pier deck top (above the ~0 waterline)
PILING_COLOR = (0.20, 0.16, 0.12)  # dark weathered post
PLANK_COLOR = (0.36, 0.27, 0.18)   # sun-bleached plank
TIRE_COLOR = (0.06, 0.06, 0.07)    # black rubber fender / rope


class Town:
    def __init__(self, app):
        self.app = app
        self.program = app.shader_program.model
        self.home = next((i for i in app.islands.islands if i.kind == 'home'), None)
        self.npc_spots = []
        self.houses = []

        md = MeshData()
        self._prop_models = {}          # name -> Model (loaded once, reused per instance)
        self.instances = []             # (name, m_model)
        if self.home is not None:
            self._build(md, self.home)
            self._dress(self.home)
        self.mesh = Mesh(app.ctx, self.program, md.array(), '3f 3f 3f',
                         ('in_position', 'in_normal', 'in_color'))
        self.m_model = glm.mat4(1.0)

    # ---------------------------------------------------------------- procedural mesh
    def _build(self, md, home):
        rng = random.Random(1234)
        cx, cz, gy = home.position.x, home.position.z, home.land_y
        ring = home.radius * 0.30
        n = cfg.TOWN_HOUSE_COUNT
        for i in range(n):
            a = (i / n) * math.tau + rng.uniform(-0.25, 0.25)
            r = ring * rng.uniform(0.6, 1.1)
            x, z = cx + math.cos(a) * r, cz + math.sin(a) * r
            self.houses.append((x, z))
            w, d, h = rng.uniform(1.2, 1.8), rng.uniform(1.2, 1.8), rng.uniform(1.4, 2.0)
            md.box(x, gy + h * 0.5, z, w, h * 0.5, d, cfg.HOUSE_WALL_COLOR)
            md.gable_roof(x, gy + h, z, w * 1.12, d * 1.12, rng.uniform(0.7, 1.1),
                          cfg.HOUSE_ROOF_COLOR)
            self.npc_spots.append(glm.vec3(x + math.cos(a) * 2.6, gy, z + math.sin(a) * 2.6))

        self._build_dock(md, home)

    # ---------------------------------------------------- Dredge-style pier (south, -z)
    def _build_dock(self, md, home):
        cx, cz = home.position.x, home.position.z
        z0 = cz - 0.805 * home.radius      # landward end, on the dry shelf
        z1 = cz - 0.997 * home.radius      # T-head inner edge; head reaches out to the moored boat
        y0, y1 = home.land_y, DECK_Y       # gangway slopes from the shelf down to the water
        hw = 1.6

        def deck_y(z):
            t = max(0.0, min(1.0, (z - z0) / (z1 - z0)))
            return y0 + (y1 - y0) * t

        # slatted plank walkway (small gaps read as weathered boards)
        n = 22
        plank_hz = abs(z1 - z0) / n * 0.42
        for k in range(n):
            z = z0 + (z1 - z0) * (k + 0.5) / n
            md.box(cx, deck_y(z), z, hw, 0.10, plank_hz, PLANK_COLOR)
        # side pilings down the walkway
        for k in range(7):
            z = z0 + (z1 - z0) * (k + 0.5) / 7
            for px in (cx - hw - 0.12, cx + hw + 0.12):
                self._piling(md, px, z, deck_y(z) + 0.5)

        # T-head platform at the seaward end (boat lies alongside its seaward face)
        hz = 1.6
        zc = z1 - hz
        md.box(cx, y1, zc, 6.0, 0.10, hz, PLANK_COLOR)
        for hx in (-6.0, -2.0, 2.0, 6.0):
            for sz in (zc - hz, zc + hz):
                self._piling(md, cx + hx, sz, y1 + 0.5)

        # mooring bollards + tire fenders + sagging rope along the seaward face
        face_z = zc - hz
        bollards = [cx - 4.0, cx, cx + 4.0]
        for bx in bollards:
            md.box(bx, y1 + 0.45, face_z, 0.18, 0.45, 0.18, PILING_COLOR)
        for bx in (cx - 2.0, cx + 2.0):
            self._tire(md, bx, y1 - 0.15, face_z - 0.06)
        for a, b in zip(bollards[:-1], bollards[1:], strict=True):
            self._rope(md, a, b, y1 + 0.72, face_z)

        # lanterns down the walkway + at the T-head's landward corners
        for k in range(4):
            z = z0 + (z1 - z0) * (k + 0.7) / 4
            self._lamp(md, cx + hw + 0.35, deck_y(z), z)
        self._lamp(md, cx - 6.0, y1, zc + hz)
        self._lamp(md, cx + 6.0, y1, zc + hz)

        # fishing clutter on the deck (existing CC0 props, explicit deck y)
        self._place('barrel.glb', cx - 4.6, zc + 0.6, 1.2, 0.3, y=y1)
        self._place('crate.glb', cx + 4.7, zc - 0.5, 1.2, 0.8, y=y1)
        self._place('crate-bottles.glb', cx + 5.0, zc + 0.8, 1.1, 0.0, y=y1)
        mz = (z0 + z1) * 0.5
        self._place('barrel.glb', cx + hw - 0.5, mz, 1.1, 0.0, y=deck_y(mz))

        # weathered pilings standing in the water around the pier (à la docks3)
        rng = random.Random(7)
        for _ in range(9):
            px = cx + rng.uniform(-15, 15)
            pz = z1 + rng.uniform(-7, 9)
            if abs(px - cx) < hw + 1.5 and pz > face_z - 1.0:   # keep clear of the deck
                px += (hw + 7.0) * (1 if px >= cx else -1)
            self._piling(md, px, pz, rng.uniform(0.6, 1.9),
                         lean=rng.uniform(0.0, 0.5), lean_dir=rng.uniform(0.0, math.tau))

    def _piling(self, md, x, z, top_y, base_y=-3.5, r=0.16, lean=0.0, lean_dir=0.0):
        tx, tz = x + lean * math.cos(lean_dir), z + lean * math.sin(lean_dir)
        b = [(x - r, base_y, z - r), (x + r, base_y, z - r),
             (x + r, base_y, z + r), (x - r, base_y, z + r)]
        t = [(tx - r, top_y, tz - r), (tx + r, top_y, tz - r),
             (tx + r, top_y, tz + r), (tx - r, top_y, tz + r)]
        for i in range(4):
            j = (i + 1) % 4
            md.quad(b[i], b[j], t[j], t[i], PILING_COLOR)
        md.quad(t[0], t[1], t[2], t[3], PILING_COLOR)

    def _tire(self, md, cx, cy, cz, ro=0.36, ri=0.20, dz=0.12, seg=8):
        """A low-poly rubber fender: a dark thick ring hung on the dock face (faces -z)."""
        zf, zb = cz + dz, cz - dz
        for i in range(seg):
            a0, a1 = math.tau * i / seg, math.tau * (i + 1) / seg
            o0 = (cx + ro * math.cos(a0), cy + ro * math.sin(a0))
            o1 = (cx + ro * math.cos(a1), cy + ro * math.sin(a1))
            i0 = (cx + ri * math.cos(a0), cy + ri * math.sin(a0))
            i1 = (cx + ri * math.cos(a1), cy + ri * math.sin(a1))
            md.quad((*o0, zf), (*o1, zf), (*i1, zf), (*i0, zf), TIRE_COLOR)   # front
            md.quad((*o0, zb), (*i0, zb), (*i1, zb), (*o1, zb), TIRE_COLOR)   # back
            md.quad((*o0, zb), (*o1, zb), (*o1, zf), (*o0, zf), TIRE_COLOR)   # outer rim
            md.quad((*i0, zf), (*i1, zf), (*i1, zb), (*i0, zb), TIRE_COLOR)   # inner rim

    def _rope(self, md, x0, x1, y, z, sag=0.32, seg=5, r=0.045):
        """A sagging rope (thin ribbon) strung between two bollards along the dock face."""
        for i in range(seg):
            t0, t1 = i / seg, (i + 1) / seg
            xa, xb = x0 + (x1 - x0) * t0, x0 + (x1 - x0) * t1
            ya = y - sag * 4.0 * t0 * (1.0 - t0)
            yb = y - sag * 4.0 * t1 * (1.0 - t1)
            md.quad((xa, ya - r, z), (xb, yb - r, z), (xb, yb + r, z), (xa, ya + r, z), TIRE_COLOR)

    def _lamp(self, md, x, gy, z):
        md.box(x, gy + 0.9, z, 0.08, 0.9, 0.08, (0.20, 0.16, 0.12))     # post
        md.box(x, gy + 1.9, z, 0.18, 0.18, 0.18, (1.0, 0.85, 0.5))      # warm lamp (bloom glow)

    # ------------------------------------------------------------------ CC0 props
    def _place(self, name, x, z, scale, yaw=0.0, y=None):
        if name not in self._prop_models:
            self._prop_models[name] = Model(self.app.ctx, self.program, _prop_path(name))
        gy = self.home.ground_y(x, z) if y is None else y
        m = glm.translate(glm.mat4(1.0), glm.vec3(x, gy, z))
        m = glm.rotate(m, yaw, glm.vec3(0, 1, 0))
        m = glm.scale(m, glm.vec3(scale))
        self.instances.append((name, m))

    def _dress(self, home):
        rng = random.Random(99)
        cx, cz = home.position.x, home.position.z
        self._place('tower-watch.glb', cx, cz, 2.6)                     # central landmark
        self._place('flag.glb', cx + 4.0, cz + 2.0, 2.2, 0.6)
        for (hx, hz) in self.houses:                                    # clutter by the houses
            if rng.random() < 0.8:
                prop = rng.choice(['barrel.glb', 'crate.glb', 'crate-bottles.glb', 'chest.glb'])
                self._place(prop, hx + rng.uniform(-2.2, 2.2), hz + rng.uniform(-2.2, 2.2),
                            1.3, rng.uniform(0, math.tau))
        for k in range(7):                                             # fences line the path
            z = cz - 6.0 - k * 4.0
            self._place('fence_simple.glb', cx - 3.2, z, 1.6, math.pi / 2)
            self._place('fence_simple.glb', cx + 3.2, z, 1.6, math.pi / 2)

    def render(self):
        if self.home is None:
            return
        self.program['m_model'].write(self.m_model)
        self.mesh.render()
        for name, m in self.instances:
            model = self._prop_models[name]
            model.m_model = m
            model.render()


def _prop_path(name):
    p = PROPS_DIR / name
    return p if p.exists() else NATURE_DIR / name
