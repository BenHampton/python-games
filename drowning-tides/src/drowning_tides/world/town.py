"""The home island's harbor town — an organic, irregular "haunted docks" settlement at the
landward end of the pier: a ragged cobble plaza with a well, varied half-timbered buildings
scattered at mixed sizes/heights/angles with alleys between, a few landmark buildings (tavern,
warehouse, market hall), branching jetties with shacks and rowboats over the water, a beached
ship wreck, and a lighthouse beacon out on a point. Buildings are assembled from the CC0 Kenney
Fantasy Town Kit (baked muted); boats/tower/dock/wreck are CC0 Kenney Pirate Kit. The pier itself
is procedural (`_build_dock`).
"""
import math
import random

from pyglm import glm

from drowning_tides.core.mesh import Mesh
from drowning_tides.core.meshbuilder import MeshData
from drowning_tides.core.model import MODELS_DIR, Model

PROPS_DIR = MODELS_DIR / "props"
NATURE_DIR = MODELS_DIR / "nature"
TOWN_DIR = MODELS_DIR / "town"          # CC0 Kenney Fantasy Town Kit (half-timbered modules)

DECK_Y = 0.6                       # pier deck top (above the ~0 waterline)
PILING_COLOR = (0.20, 0.16, 0.12)
PLANK_COLOR = (0.36, 0.27, 0.18)
TIRE_COLOR = (0.06, 0.06, 0.07)

TOWN_MUTE = 0.45
S = 2.8                            # world size of one 1-unit kit module (a building floor)
PLASTER = (0.42, 0.38, 0.32)
ROOF_COLORS = [(0.34, 0.22, 0.17), (0.30, 0.30, 0.31), (0.26, 0.24, 0.22)]  # tile / slate / dark
PLAZA_COLOR = (0.34, 0.33, 0.32)

WALLS_WOOD = ['wall-wood.glb', 'wall-wood-window-shutters.glb', 'wall-wood-window-glass.glb',
              'wall-wood-detail-cross.glb', 'wall-wood-window-small.glb']
WALLS_STONE = ['wall.glb', 'wall-window-shutters.glb', 'wall-window-glass.glb',
               'wall-detail-cross.glb', 'wall-half.glb']
DOORS = {'wood': 'wall-wood-door.glb', 'stone': 'wall-door.glb'}


class Town:
    def __init__(self, app):
        self.app = app
        self.program = app.shader_program.model
        self.home = next((i for i in app.islands.islands if i.kind == 'home'), None)
        self.npc_spots = []

        md = MeshData()
        self._models = {}               # (path, mute) -> Model
        self.instances = []             # (key, m_model)
        self.colliders = []             # solid AABBs (min_x, min_z, max_x, max_z)
        self.flat_decks = []            # walkable flat plank rects (x0, z0, x1, z1, y)
        self._pier = None               # sloped main-pier walkway (cx, hw, z_far, z_near)
        if self.home is not None:
            self._build(md, self.home)
        self.mesh = Mesh(app.ctx, self.program, md.array(), '3f 3f 3f',
                         ('in_position', 'in_normal', 'in_color'))
        self.m_model = glm.mat4(1.0)

    # ------------------------------------------------------------------ layout
    def _build(self, md, home):
        cx, cz, gy = home.position.x, home.position.z, home.land_y
        z_dock = cz - 0.805 * home.radius            # pier's landward end
        px, pz = cx - 2.0, z_dock + 11.0             # plaza centre, just off the dock
        self.plaza = glm.vec2(px, pz)

        # ragged cobble plaza + off-centre well
        md.box(px, gy + 0.12, pz, 11.0, 0.12, 10.0, PLAZA_COLOR)
        self._kit('fountain-round.glb', px - 3.0, pz - 1.0, 2.0, y=gy)
        self._kit('fountain-center.glb', px - 3.0, pz - 1.0, 2.0, y=gy)
        self._solid(px - 3.0, pz - 1.0, 2.0, 2.0)

        # landmark buildings (assembled bigger to anchor the town)
        self._building(md, cx + 11.0, pz + 4.0, 4, 3, 3, self._face(cx + 11.0, pz + 4.0),
                       'wood', banner=True)                                    # tavern/inn
        self._building(md, cx - 15.0, pz + 2.0, 5, 3, 2, self._face(cx - 15.0, pz + 2.0),
                       'stone')                                                # warehouse
        self._building(md, cx + 2.0, pz + 13.0, 4, 2, 3, self._face(cx + 2.0, pz + 13.0),
                       'stone')                                                # market hall

        # organic scatter of varied houses, leaving alley gaps
        self._scatter_houses(md, home, n=20)

        # over-water sprawl: branching jetties, shacks, rowboats, wreck, lighthouse
        self._build_dock(md, home)
        self._build_harbor(md, home, z_dock)
        self._dress(home, px, pz)

    def _face(self, x, z):
        """Yaw whose front normal points from (x,z) toward the plaza (door faces the square)."""
        d = self.plaza - glm.vec2(x, z)
        return math.atan2(d.x, d.y)

    def _scatter_houses(self, md, home, n):
        cx, cz, R = home.position.x, home.position.z, home.radius
        rng = random.Random(20260615)
        placed = [(self.plaza.x, self.plaza.y, 11.0)]          # avoid the plaza
        built = 0
        for _ in range(400):
            if built >= n:
                break
            ang = rng.uniform(0.0, math.tau)
            rad = rng.uniform(13.0, 42.0)
            x = self.plaza.x + math.cos(ang) * rad
            z = self.plaza.y + math.sin(ang) * rad
            if math.hypot(x - cx, z - cz) > 0.78 * R or z > cz - 6:   # stay on the south shelf
                continue
            w = rng.choice([2, 2, 3, 3, 4])
            d = rng.choice([2, 2, 3])
            rr = max(w, d) * S * 0.55
            if any(math.hypot(x - bx, z - bz) < rr + br + rng.uniform(1.5, 3.5)
                   for (bx, bz, br) in placed):
                continue
            placed.append((x, z, rr))
            floors = rng.choice([2, 2, 3, 3])               # mostly 2-3 storeys, no sheds
            yaw = self._face(x, z) + rng.uniform(-0.35, 0.35)
            self._building(md, x, z, w, d, floors, yaw, rng.choice(['wood', 'wood', 'stone']))
            built += 1

    # ------------------------------------------------------------- building assembler
    def _building(self, md, cx, cz, w_units, d_units, floors, yaw, style='wood', banner=False):
        gy = self.home.land_y
        bx, bz = w_units * S * 0.5, d_units * S * 0.5      # half width / depth (local)
        h = floors * S
        c, s = math.cos(yaw), math.sin(yaw)

        def L(lx, lz, ly):                                  # local (width,depth) -> world
            return (cx + lx * c + lz * s, ly, cz - lx * s + lz * c)

        self._rot_box(md, L, bx, bz, gy - 0.4, gy + h, PLASTER)
        rcol = ROOF_COLORS[(w_units + floors) % len(ROOF_COLORS)]
        self._rot_gable(md, L, bx * 1.04, bz * 1.04, gy + h, S * 0.62, rcol)

        # clad the plaza-facing front with kit wall panels (door + windows), per floor
        pyaw = math.atan2(-c, s)                            # panel yaw so its face points front
        walls = WALLS_WOOD if style == 'wood' else WALLS_STONE
        prng = random.Random(int(cx * 7 + cz * 13))
        for f in range(floors):
            for i in range(w_units):
                lx = (i - (w_units - 1) / 2.0) * S
                wx, _, wz = L(lx, bz - 0.40 * S, 0.0)
                if f == 0 and i == w_units // 2:
                    piece = DOORS[style]
                else:
                    piece = prng.choice(walls)
                self._kit(piece, wx, wz, S, yaw=pyaw, y=gy + f * S)
        dx, _, dz = L(0.0, bz + 1.6, 0.0)
        self.npc_spots.append(glm.vec3(dx, gy, dz))
        if banner:
            self._kit('banner-red.glb', *self._xz(L(bx - 0.3, bz, 0.0)), S, y=gy + h - S)
        self._chimney(md, L, bx, bz, gy + h)
        # collider: AABB of the rotated footprint
        xs = [cx + lx * c + lz * s for lx in (-bx, bx) for lz in (-bz, bz)]
        zs = [cz - lx * s + lz * c for lx in (-bx, bx) for lz in (-bz, bz)]
        self.colliders.append((min(xs), min(zs), max(xs), max(zs)))

    @staticmethod
    def _xz(world_pt):
        return world_pt[0], world_pt[2]

    def _chimney(self, md, L, bx, bz, y_top):
        x, _, z = L(bx * 0.5, -bz * 0.4, 0.0)
        self._kit('chimney.glb', x, z, S * 0.5, y=y_top)

    def _rot_box(self, md, L, bx, bz, y0, y1, color):
        b = [L(-bx, -bz, y0), L(bx, -bz, y0), L(bx, bz, y0), L(-bx, bz, y0)]
        t = [L(-bx, -bz, y1), L(bx, -bz, y1), L(bx, bz, y1), L(-bx, bz, y1)]
        for i in range(4):
            j = (i + 1) % 4
            md.quad(b[i], b[j], t[j], t[i], color)
        md.quad(t[0], t[1], t[2], t[3], color)

    def _rot_gable(self, md, L, bx, bz, y, rh, color):
        md.quad(L(-bx, bz, y), L(bx, bz, y), L(bx, 0, y + rh), L(-bx, 0, y + rh), color)
        md.quad(L(bx, -bz, y), L(-bx, -bz, y), L(-bx, 0, y + rh), L(bx, 0, y + rh), color)
        md.tri(L(-bx, bz, y), L(-bx, 0, y + rh), L(-bx, -bz, y), color)
        md.tri(L(bx, -bz, y), L(bx, 0, y + rh), L(bx, bz, y), color)

    # ------------------------------------------------------------- harbor / over-water
    def _build_harbor(self, md, home, z_dock):
        cx = home.position.x
        # branching jetties off the main pier, each a walkable plank path to a dock shack
        for sgn, jz in ((1, z_dock - 7.0), (-1, z_dock - 12.0)):
            x_end = cx + sgn * 13.0
            x0, x1 = sorted((cx, x_end))
            md.box((x0 + x1) / 2, DECK_Y, jz, abs(x1 - x0) / 2, 0.10, 1.4, PLANK_COLOR)  # planks
            self.flat_decks.append((x0 - 1.0, jz - 1.4, x1 + 1.0, jz + 1.4, DECK_Y))     # walkable
            for k in range(7):
                jx = cx + sgn * (1.5 + k * 1.8)
                self._piling(md, jx, jz - 1.3, DECK_Y + 0.4)
                self._piling(md, jx, jz + 1.3, DECK_Y + 0.4)
            self._shack(md, x_end + sgn * 2.5, jz)
            self._place('boat-row-small.glb', x_end + sgn * 3.0, jz + 3.0, 1.3,
                        yaw=rng_yaw(jz), y=-0.15)
        # a half-sunk wreck looming in the water + the lighthouse beacon on a point
        self._place('ship-wreck.glb', cx - 22.0, z_dock - 14.0, 1.1, yaw=2.3, y=-1.4)
        self._lighthouse(md, cx + 17.0, z_dock - 18.0)

    def _shack(self, md, x, z, half=2.6):
        """A small weathered hut on a walkable wooden dock platform out over the water."""
        md.box(x, DECK_Y, z, half, 0.10, half, PLANK_COLOR)              # plank platform
        self.flat_decks.append((x - half, z - half, x + half, z + half, DECK_Y))
        for cxp in (x - half + 0.3, x + half - 0.3):                    # corner pilings
            for czp in (z - half + 0.3, z + half - 0.3):
                self._piling(md, cxp, czp, DECK_Y + 0.3)
        gy = DECK_Y + 0.05
        for (lx, lz, pyaw) in ((0, half - 0.4, -math.pi / 2), (0, -(half - 0.4), math.pi / 2),
                               (half - 0.4, 0, math.pi), (-(half - 0.4), 0, 0.0)):
            self._kit('wall-wood.glb', x + lx, z + lz, S, yaw=pyaw, y=gy)

        def L(lx, lz, ly):
            return (x + lx, ly, z + lz)
        self._rot_gable(md, L, half * 0.95, half * 0.95, gy + S, 1.1, ROOF_COLORS[2])

    def _lighthouse(self, md, x, z):
        self._place('structure-platform-dock.glb', x, z, 2.4, y=0.0)
        self._place('tower-complete-large.glb', x, z, 1.7, y=0.5)
        top = 0.5 + 10.22 * 1.7
        md.box(x, top + 0.5, z, 1.0, 0.6, 1.0, (1.0, 0.92, 0.62))     # glowing lamp room (bloom)
        self._solid(x, z, 3.4, 3.4)

    def _dress(self, home, px, pz):
        rng = random.Random(7)
        gy = home.land_y
        self._kit('stall-red.glb', px + 4.0, pz - 2.0, S, yaw=0.4, y=gy)
        self._kit('stall-green.glb', px - 5.5, pz + 3.0, S, yaw=2.6, y=gy)
        self._kit('cart.glb', px + 6.5, pz + 1.0, S, yaw=1.0, y=gy)
        for _ in range(7):                                            # lanterns about the lanes
            a, r = rng.uniform(0, math.tau), rng.uniform(7.0, 26.0)
            lx, lz = px + math.cos(a) * r, pz + math.sin(a) * r
            if math.hypot(lx - home.position.x, lz - home.position.z) < 0.80 * home.radius:
                self._kit('lantern.glb', lx, lz, 1.7, y=home.ground_y(lx, lz))
        for _ in range(6):
            a, r = rng.uniform(0, math.tau), rng.uniform(8.0, 24.0)
            bx, bz = px + math.cos(a) * r, pz + math.sin(a) * r
            self._place(rng.choice(['barrel.glb', 'crate.glb']), bx, bz, 1.2,
                        rng.uniform(0, math.tau), y=home.ground_y(bx, bz))

    # ------------------------------------------------------------- model instancing
    def _solid(self, cx, cz, hx, hz):
        self.colliders.append((cx - hx, cz - hz, cx + hx, cz + hz))

    def collide(self, x, z, radius):
        return resolve_town_collision(x, z, self.colliders, radius)

    def deck_height(self, x, z):
        """Plank height at (x, z) if standing over a walkable dock surface, else None."""
        ly = self.home.land_y if self.home is not None else 0.0
        return deck_height_at(x, z, self._pier, self.flat_decks, ly, DECK_Y)

    def _inst(self, path, x, z, scale, yaw=0.0, y=None, mute=0.0):
        key = (str(path), mute)
        if key not in self._models:
            self._models[key] = Model(self.app.ctx, self.program, path, mute=mute)
        gy = self.home.ground_y(x, z) if y is None else y
        m = glm.translate(glm.mat4(1.0), glm.vec3(x, gy, z))
        m = glm.rotate(m, yaw, glm.vec3(0, 1, 0))
        m = glm.scale(m, glm.vec3(scale))
        self.instances.append((key, m))

    def _kit(self, name, x, z, scale, yaw=0.0, y=None):
        self._inst(TOWN_DIR / name, x, z, scale, yaw, y, mute=TOWN_MUTE)

    def _place(self, name, x, z, scale, yaw=0.0, y=None):
        self._inst(_prop_path(name), x, z, scale, yaw, y, mute=0.0)

    # ---------------------------------------------------- Dredge-style pier (south, -z)
    def _build_dock(self, md, home):
        cx, cz = home.position.x, home.position.z
        z0 = cz - 0.805 * home.radius
        z1 = cz - 0.997 * home.radius
        y0, y1 = home.land_y, DECK_Y
        hw = 2.0

        def deck_y(z):
            t = max(0.0, min(1.0, (z - z0) / (z1 - z0)))
            return y0 + (y1 - y0) * t

        self._pier = (cx, hw, z1, z0)            # walkable sloped walkway (far z1 -> near z0)
        n = 22
        plank_hz = abs(z1 - z0) / n * 0.42
        for k in range(n):
            z = z0 + (z1 - z0) * (k + 0.5) / n
            md.box(cx, deck_y(z), z, hw, 0.10, plank_hz, PLANK_COLOR)
        for k in range(7):
            z = z0 + (z1 - z0) * (k + 0.5) / 7
            for px in (cx - hw - 0.12, cx + hw + 0.12):
                self._piling(md, px, z, deck_y(z) + 0.5)

        hz = 2.0
        hxw = 7.0                                            # T-head half-width
        zc = z1 - hz
        md.box(cx, y1, zc, hxw, 0.10, hz, PLANK_COLOR)
        self.flat_decks.append((cx - hxw, zc - hz, cx + hxw, zc + hz, y1))   # walkable T-head
        for hx in (-hxw, -2.5, 2.5, hxw):
            for sz in (zc - hz, zc + hz):
                self._piling(md, cx + hx, sz, y1 + 0.5)

        face_z = zc - hz
        bollards = [cx - 5.0, cx, cx + 5.0]
        for bx in bollards:
            md.box(bx, y1 + 0.45, face_z, 0.18, 0.45, 0.18, PILING_COLOR)
        for bx in (cx - 2.5, cx + 2.5):
            self._tire(md, bx, y1 - 0.15, face_z - 0.06)
        for a, b in zip(bollards[:-1], bollards[1:], strict=True):
            self._rope(md, a, b, y1 + 0.72, face_z)

        for k in range(4):
            z = z0 + (z1 - z0) * (k + 0.7) / 4
            self._lamp(md, cx + hw + 0.35, deck_y(z), z)
        self._lamp(md, cx - hxw, y1, zc + hz)
        self._lamp(md, cx + hxw, y1, zc + hz)

        self._place('barrel.glb', cx - 4.6, zc + 0.6, 1.2, 0.3, y=y1)
        self._place('crate.glb', cx + 4.7, zc - 0.5, 1.2, 0.8, y=y1)

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
        zf, zb = cz + dz, cz - dz
        for i in range(seg):
            a0, a1 = math.tau * i / seg, math.tau * (i + 1) / seg
            o0 = (cx + ro * math.cos(a0), cy + ro * math.sin(a0))
            o1 = (cx + ro * math.cos(a1), cy + ro * math.sin(a1))
            i0 = (cx + ri * math.cos(a0), cy + ri * math.sin(a0))
            i1 = (cx + ri * math.cos(a1), cy + ri * math.sin(a1))
            md.quad((*o0, zf), (*o1, zf), (*i1, zf), (*i0, zf), TIRE_COLOR)
            md.quad((*o0, zb), (*i0, zb), (*i1, zb), (*o1, zb), TIRE_COLOR)
            md.quad((*o0, zb), (*o1, zb), (*o1, zf), (*o0, zf), TIRE_COLOR)
            md.quad((*i0, zf), (*i1, zf), (*i1, zb), (*i0, zb), TIRE_COLOR)

    def _rope(self, md, x0, x1, y, z, sag=0.32, seg=5, r=0.045):
        for i in range(seg):
            t0, t1 = i / seg, (i + 1) / seg
            xa, xb = x0 + (x1 - x0) * t0, x0 + (x1 - x0) * t1
            ya = y - sag * 4.0 * t0 * (1.0 - t0)
            yb = y - sag * 4.0 * t1 * (1.0 - t1)
            md.quad((xa, ya - r, z), (xb, yb - r, z), (xb, yb + r, z), (xa, ya + r, z), TIRE_COLOR)

    def _lamp(self, md, x, gy, z):
        md.box(x, gy + 0.9, z, 0.08, 0.9, 0.08, (0.20, 0.16, 0.12))
        md.box(x, gy + 1.9, z, 0.18, 0.18, 0.18, (1.0, 0.85, 0.5))

    def render(self):
        if self.home is None:
            return
        self.program['m_model'].write(self.m_model)
        self.mesh.render()
        for key, m in self.instances:
            model = self._models[key]
            model.m_model = m
            model.render()


def rng_yaw(seed):
    return (seed * 0.37) % math.tau


def _prop_path(name):
    p = PROPS_DIR / name
    return p if p.exists() else NATURE_DIR / name


def deck_height_at(x, z, pier, flat_decks, land_y, deck_top):
    """Walkable plank height at (x, z): the sloped main pier (cx, hw, z_far, z_near) plus any flat
    deck rect (x0, z0, x1, z1, y). Returns the highest deck under the point, or None. Pure."""
    y = None
    if pier is not None:
        cx, hw, z_far, z_near = pier
        if cx - hw <= x <= cx + hw and z_far <= z <= z_near:
            t = max(0.0, min(1.0, (z - z_near) / (z_far - z_near)))
            y = land_y + (deck_top - land_y) * t
    for (x0, z0, x1, z1, fy) in flat_decks:
        if x0 <= x <= x1 and z0 <= z <= z1:
            y = fy if y is None else max(y, fy)
    return y


def resolve_town_collision(x, z, colliders, radius):
    """Push a circle (centre x,z, radius) out of any solid AABB footprint. Two passes so a push
    into a neighbour resolves. Pure -> unit-testable without a GL context."""
    for _ in range(2):
        for (ax0, az0, ax1, az1) in colliders:
            cxc = min(max(x, ax0), ax1)
            czc = min(max(z, az0), az1)
            dx, dz = x - cxc, z - czc
            d2 = dx * dx + dz * dz
            if d2 >= radius * radius:
                continue
            if d2 > 1e-9:
                d = math.sqrt(d2)
                x += dx / d * (radius - d)
                z += dz / d * (radius - d)
            else:
                left, right, back, front = x - ax0, ax1 - x, z - az0, az1 - z
                m = min(left, right, back, front)
                if m == left:
                    x = ax0 - radius
                elif m == right:
                    x = ax1 + radius
                elif m == back:
                    z = az0 - radius
                else:
                    z = az1 + radius
    return x, z
