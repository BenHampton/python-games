"""The home island's harbor town — a sealed walled courtyard. Buildings sit edge-to-edge forming
three walls of a rectangular courtyard, with the alley gaps plugged by colliding props (fences,
hedges, carts, crate/barrel stacks); the opening faces the dock, where stairs climb from the boat
pier up into the courtyard. The well + market stalls sit in the centre. The wall ring + the water
seal the player to the dock + courtyard — the rest of the island is closed off. Buildings are
assembled from the CC0 Kenney Fantasy Town Kit (baked muted); boats/tower/dock/wreck are CC0
Kenney Pirate Kit.
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

DECK_Y = 0.6                       # low pier/jetty deck (just above the ~0 waterline)
PILING_COLOR = (0.20, 0.16, 0.12)
PLANK_COLOR = (0.36, 0.27, 0.18)   # shared dock colour (pier, jetties, stairs)
TIRE_COLOR = (0.06, 0.06, 0.07)

TOWN_MUTE = 0.45
S = 2.8                            # world size of one 1-unit kit module (a building floor)
PLASTER = (0.42, 0.38, 0.32)
ROOF_COLORS = [(0.34, 0.22, 0.17), (0.30, 0.30, 0.31), (0.26, 0.24, 0.22)]
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
        self.ramps = []                 # walkable ramps (x0, z0, x1, z1, y_lo, y_hi, axis)
        self.boat_blockers = []         # over-water structures the boat collides with (AABBs)
        self.dock_anchor = None         # glm.vec2 mooring point (pier T-head face); docking gate
        self._t_head_z = None
        if self.home is not None:
            self._build(md, self.home)
            # the boat can't sail through the pier/jetties/landing planks (plus the lighthouse,
            # appended in _lighthouse) — the courtyard walls sit inland behind the island disc.
            self.boat_blockers += [(x0, z0, x1, z1) for (x0, z0, x1, z1, _y) in self.flat_decks]
        self.mesh = Mesh(app.ctx, self.program, md.array(), '3f 3f 3f',
                         ('in_position', 'in_normal', 'in_color'))
        self.m_model = glm.mat4(1.0)

    # ------------------------------------------------------------------ layout
    def _build(self, md, home):
        cx, cz, gy = home.position.x, home.position.z, home.land_y
        R = home.radius
        hx = 18.0
        z_open = cz - 0.79 * R               # courtyard opening (dock side, near the shelf edge)
        z_back = z_open + 32.0               # north/back wall (inland)
        z_edge = cz - 0.84 * R               # shelf edge (cobble the apron out to the stair top)
        midz = (z_open + z_back) / 2
        self.court = (cx, hx, z_open, z_back)

        # cobble floor, extended south over the flat-shelf apron to where the stairs begin
        md.box(cx, gy + 0.12, (z_edge + z_back) / 2, hx, 0.12, (z_back - z_edge) / 2, PLAZA_COLOR)
        self._courtyard_walls(md, home, hx, z_open, z_back)

        # centre: well + a cluster of market stalls
        self._kit('fountain-round.glb', cx, midz, 2.2, y=gy)
        self._kit('fountain-center.glb', cx, midz, 2.2, y=gy)
        self._solid(cx, midz, 2.2, 2.2)
        self._kit('stall-red.glb', cx - 6.0, midz - 4.0, S, yaw=0.3, y=gy)
        self._kit('stall-green.glb', cx + 6.0, midz - 4.0, S, yaw=2.8, y=gy)
        self._kit('stall-stool.glb', cx - 6.0, midz + 4.0, S, y=gy)
        self._kit('cart.glb', cx + 6.0, midz + 4.0, S, yaw=1.0, y=gy)
        for (lx, lz) in ((-hx + 2, z_open + 3), (hx - 2, z_open + 3),
                         (-hx + 2, z_back - 3), (hx - 2, z_back - 3)):
            self._kit('lantern.glb', cx + lx, lz, 1.7, y=gy)

        self._build_dock(md, home, z_open)
        self._build_harbor(md, home)

    def _courtyard_walls(self, md, home, hx, z_open, z_back):
        cx = home.position.x
        rng = random.Random(777)
        self._wall(md, 'x', z_back, cx - hx, cx + hx, math.pi, rng)          # north (back)
        # east + west use the SAME rolled run, mirrored about cx -> exact left-right symmetry
        side = self._roll_wall(z_back - z_open, rng)
        self._lay_wall(md, 'z', cx + hx, z_open, z_back, -math.pi / 2, *side, rng)
        self._lay_wall(md, 'z', cx - hx, z_open, z_back, math.pi / 2, *side, rng)
        gy = home.land_y
        for sgn in (1, -1):
            # seal the back corners where the north + side walls meet (hedge + crate cluster)
            self._solid(cx + sgn * hx, z_back, 4.5, 4.5)
            self._kit('hedge.glb', cx + sgn * hx, z_back, S * 0.85, y=gy)
            self._place('crate.glb', cx + sgn * (hx - 1.5), z_back - 1.5, 1.5,
                        yaw=0.4, y=gy)
            # short fence stubs flanking the opening, funnelling the south side to the stairs
            self._blocker(md, 'z', cx + sgn * hx, z_open - 4.0, z_open - 0.5, rng)

    def _roll_wall(self, span, rng):
        """Roll a sequence of buildings + inter-gaps that fits within a wall span."""
        items, gaps_between, total = [], [], 0.0
        while True:
            w, d = rng.choice([2, 3, 3, 4]), rng.choice([2, 3])
            bw = w * S
            nxt_gap = rng.uniform(1.6, 2.8) if items else 0.0
            if total + nxt_gap + bw > span - 1.0:
                break
            if items:
                gaps_between.append(nxt_gap)
                total += nxt_gap
            items.append((w, d, rng.choice([2, 3, 3]), rng.choice(['wood', 'wood', 'stone'])))
            total += bw
        return items, gaps_between, total

    def _lay_wall(self, md, axis, fixed, lo, hi, face_yaw, items, gaps_between, total, rng):
        """Place a rolled wall run centred within [lo, hi] (equal end-margins), fronts facing into
        the courtyard, with colliding props plugging the gaps."""
        fnx, fnz = math.sin(face_yaw), math.cos(face_yaw)
        if not items:
            self._blocker(md, axis, fixed, lo, hi, rng)
            return
        t = lo + ((hi - lo) - total) / 2.0
        spans = []
        for k, (w, d, floors, style) in enumerate(items):
            if k > 0:
                t += gaps_between[k - 1]
            bw = w * S
            mt = t + bw / 2
            ax, az = (mt, fixed) if axis == 'x' else (fixed, mt)
            cxb, czb = ax - fnx * (d * S * 0.5), az - fnz * (d * S * 0.5)
            self._building(md, cxb, czb, w, d, floors, face_yaw, style)
            spans.append((t, t + bw))
            t += bw
        gaps = [(lo, spans[0][0])]
        gaps += [(spans[i][1], spans[i + 1][0]) for i in range(len(spans) - 1)]
        gaps.append((spans[-1][1], hi))
        for (g0, g1) in gaps:
            if g1 - g0 > 0.4:
                self._blocker(md, axis, fixed, g0, g1, rng)

    def _wall(self, md, axis, fixed, lo, hi, face_yaw, rng):
        self._lay_wall(md, axis, fixed, lo, hi, face_yaw, *self._roll_wall(hi - lo, rng), rng)

    def _blocker(self, md, axis, fixed, g0, g1, rng):
        """Plug an alley gap with a colliding prop (fence/hedge line, cart, or crate stack)."""
        gy = self.home.land_y
        gw = g1 - g0
        gc = (g0 + g1) / 2
        x, z = (gc, fixed) if axis == 'x' else (fixed, gc)
        if axis == 'x':
            self._solid(x, z, gw / 2 + 0.3, 1.1)
        else:
            self._solid(x, z, 1.1, gw / 2 + 0.3)
        # fence/hedge/cart models span their local Z, so align that span with the wall axis
        span_yaw = math.pi / 2 if axis == 'x' else 0.0
        pick = rng.random()
        if pick < 0.5:                                   # fence / hedge line
            prop = rng.choice(['fence.glb', 'fence.glb', 'hedge.glb'])
            n = max(1, int(round(gw / 1.7)))
            for i in range(n):
                o = -gw / 2 + (i + 0.5) * (gw / n)
                fx, fz = (x + o, z) if axis == 'x' else (x, z + o)
                self._kit(prop, fx, fz, S * 0.62, yaw=span_yaw, y=gy)
        elif pick < 0.78:                                # a cart across the alley
            self._kit('cart.glb', x, z, S * 0.85, yaw=span_yaw, y=gy)
        else:                                            # crate + barrel stack
            self._place('crate.glb', x, z, 1.4, yaw=rng.uniform(0, math.tau), y=gy)
            self._place('barrel.glb', x + 0.5, z + 0.4, 1.2, y=gy)

    # ------------------------------------------------------------- building assembler
    def _building(self, md, cx, cz, w_units, d_units, floors, yaw, style='wood', banner=False):
        gy = self.home.land_y
        bx, bz = w_units * S * 0.5, d_units * S * 0.5
        h = floors * S
        c, s = math.cos(yaw), math.sin(yaw)

        def L(lx, lz, ly):
            return (cx + lx * c + lz * s, ly, cz - lx * s + lz * c)

        self._rot_box(md, L, bx, bz, gy - 0.4, gy + h, PLASTER)
        rcol = ROOF_COLORS[(w_units + floors) % len(ROOF_COLORS)]
        self._rot_gable(md, L, bx * 1.04, bz * 1.04, gy + h, S * 0.62, rcol)

        pyaw = math.atan2(-c, s)
        walls = WALLS_WOOD if style == 'wood' else WALLS_STONE
        prng = random.Random(int(cx * 7 + cz * 13))
        for f in range(floors):
            for i in range(w_units):
                lx = (i - (w_units - 1) / 2.0) * S
                wx, _, wz = L(lx, bz - 0.40 * S, 0.0)
                piece = DOORS[style] if (f == 0 and i == w_units // 2) else prng.choice(walls)
                self._kit(piece, wx, wz, S, yaw=pyaw, y=gy + f * S)
        dx, _, dz = L(0.0, bz + 1.6, 0.0)
        self.npc_spots.append(glm.vec3(dx, gy, dz))
        if banner:
            self._kit('banner-red.glb', *self._xz(L(bx - 0.3, bz, 0.0)), S, y=gy + h - S)
        self._chimney(md, L, bx, bz, gy + h)
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

    # ------------------------------------------------------------- boat pier + stairs
    def _build_dock(self, md, home, z_open):
        cx, cz, R = home.position.x, home.position.z, home.radius
        gy = home.land_y
        sw = 18.0                                    # wide stair/landing half-width (opening width)
        z_edge = cz - 0.84 * R                       # start the flight at the shelf edge, so the
        z_stair_bot = z_edge - 8.5                   # steps sit over the falling beach -> no mesh
        z_land_bot = z_stair_bot - 4.0
        # wide grand wooden staircase: shelf edge (gy) down to the landing (DECK_Y)
        self._stairs(md, cx, z_edge, z_stair_bot, gy, DECK_Y, sw, n=10)
        # wide low landing / wharf at water level, on pilings
        md.box(cx, DECK_Y - 0.11, (z_stair_bot + z_land_bot) / 2, sw, 0.11,
               abs(z_stair_bot - z_land_bot) / 2, PLANK_COLOR)
        self.flat_decks.append((cx - sw, z_land_bot, cx + sw, z_stair_bot, DECK_Y))
        for i in range(7):
            self._piling(md, cx - sw + i * (sw / 3.0), z_land_bot, DECK_Y + 0.4)
        for sz in (z_stair_bot, (z_stair_bot + z_land_bot) / 2, z_land_bot):
            self._piling(md, cx - sw, sz, DECK_Y + 0.4)
            self._piling(md, cx + sw, sz, DECK_Y + 0.4)
        # narrow boat pier from the landing centre out to the T-head
        hw = 2.5
        z1 = cz - 0.997 * R
        n = max(2, round(abs(z_land_bot - z1) / 0.95))
        stp = (z1 - z_land_bot) / n
        for k in range(n):
            za, zb = z_land_bot + stp * k, z_land_bot + stp * (k + 1)
            md.box(cx, DECK_Y - 0.11, (za + zb) / 2, hw, 0.11, abs(zb - za) / 2 - 0.05, PLANK_COLOR)
        self.flat_decks.append((cx - hw, min(z_land_bot, z1), cx + hw, max(z_land_bot, z1), DECK_Y))
        for k in range(4):
            z = z_land_bot + (z1 - z_land_bot) * (k + 0.5) / 4
            for px in (cx - hw - 0.12, cx + hw + 0.12):
                self._piling(md, px, z, DECK_Y + 0.5)

        hz, hxw = 2.0, 7.0
        zc = z1 - hz
        md.box(cx, DECK_Y, zc, hxw, 0.10, hz, PLANK_COLOR)
        self.flat_decks.append((cx - hxw, zc - hz, cx + hxw, zc + hz, DECK_Y))
        for hxp in (-hxw, -2.5, 2.5, hxw):
            for sz in (zc - hz, zc + hz):
                self._piling(md, cx + hxp, sz, DECK_Y + 0.5)
        face_z = zc - hz
        bollards = [cx - 5.0, cx, cx + 5.0]
        for bx in bollards:
            md.box(bx, DECK_Y + 0.45, face_z, 0.18, 0.45, 0.18, PILING_COLOR)
        for bx in (cx - 2.5, cx + 2.5):
            self._tire(md, bx, DECK_Y - 0.15, face_z - 0.06)
        for a, b in zip(bollards[:-1], bollards[1:], strict=True):
            self._rope(md, a, b, DECK_Y + 0.72, face_z)
        self._lamp(md, cx - hxw, DECK_Y, zc + hz)
        self._lamp(md, cx + hxw, DECK_Y, zc + hz)
        self._place('barrel.glb', cx - 4.6, zc + 0.6, 1.2, 0.3, y=DECK_Y)
        self._place('crate.glb', cx + 4.7, zc - 0.5, 1.2, 0.8, y=DECK_Y)
        self._t_head_z = z1
        self.dock_anchor = glm.vec2(cx, face_z)      # where the boat ties up; docking-range centre

    def _stairs(self, md, cx, z_top, z_bot, y_top, y_bot, hw, n=4):
        for i in range(n):
            za = z_top + (z_bot - z_top) * i / n
            zb = z_top + (z_bot - z_top) * (i + 1) / n
            yi = y_top + (y_bot - y_top) * (i + 1) / n
            md.box(cx, yi - 0.6, (za + zb) / 2, hw, 0.6, abs(zb - za) / 2, PLANK_COLOR)
        # solid sloped side stringers (read as a built flight + hide where steps meet the beach)
        yb = -0.4
        for sx in (cx - hw, cx + hw):
            md.quad((sx, y_top, z_top), (sx, y_bot, z_bot), (sx, yb, z_bot), (sx, yb, z_top),
                    PLANK_COLOR)
            md.quad((sx, yb, z_top), (sx, yb, z_bot), (sx, y_bot, z_bot), (sx, y_top, z_top),
                    PLANK_COLOR)
            self._piling(md, sx, z_bot, y_bot + 0.4)
            self._piling(md, sx, z_top, y_top - 0.4)
        self.ramps.append((cx - hw, min(z_top, z_bot), cx + hw, max(z_top, z_bot),
                           y_bot, y_top, 'z'))

    # ------------------------------------------------------------- harbor / over-water
    def _build_harbor(self, md, home):
        cx = home.position.x
        z1 = self._t_head_z
        for sgn, jz in ((1, z1 + 1.5), (-1, z1 - 1.5)):
            x_end = cx + sgn * 12.0
            x0, x1 = sorted((cx, x_end))
            md.box((x0 + x1) / 2, DECK_Y - 0.11, jz, abs(x1 - x0) / 2, 0.11, 1.4, PLANK_COLOR)
            self.flat_decks.append((x0 - 1.0, jz - 1.4, x1 + 1.0, jz + 1.4, DECK_Y))
            for k in range(7):
                jx = cx + sgn * (1.5 + k * 1.8)
                self._piling(md, jx, jz - 1.3, DECK_Y + 0.4)
                self._piling(md, jx, jz + 1.3, DECK_Y + 0.4)
            self._shack(md, x_end + sgn * 2.5, jz)
            self._place('boat-row-small.glb', x_end + sgn * 3.0, jz + 3.0, 1.3,
                        yaw=rng_yaw(jz), y=-0.15)
        self._place('ship-wreck.glb', cx - 24.0, z1 - 12.0, 1.1, yaw=2.3, y=-1.4)
        self._lighthouse(md, cx + 20.0, z1 - 14.0)

    def _shack(self, md, x, z, half=2.6):
        md.box(x, DECK_Y, z, half, 0.10, half, PLANK_COLOR)
        self.flat_decks.append((x - half, z - half, x + half, z + half, DECK_Y))
        for cxp in (x - half + 0.3, x + half - 0.3):
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
        md.box(x, top + 0.5, z, 1.0, 0.6, 1.0, (1.0, 0.92, 0.62))
        self._solid(x, z, 3.4, 3.4)
        self.boat_blockers.append((x - 3.4, z - 3.4, x + 3.4, z + 3.4))   # boat can't ram the base

    # ------------------------------------------------------------- model instancing
    def _solid(self, cx, cz, hx, hz):
        self.colliders.append((cx - hx, cz - hz, cx + hx, cz + hz))

    def collide(self, x, z, radius):
        return resolve_town_collision(x, z, self.colliders, radius)

    def collide_boat(self, x, z, radius):
        """Push the boat's disc out of the over-water dock structures. Returns (x, z, hit)."""
        nx, nz = resolve_town_collision(x, z, self.boat_blockers, radius)
        return nx, nz, abs(nx - x) > 1e-6 or abs(nz - z) > 1e-6

    def deck_height(self, x, z):
        """Plank height at (x, z) if standing over a walkable dock surface, else None."""
        return deck_height_at(x, z, self.ramps, self.flat_decks)

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

    # ------------------------------------------------------------- procedural dock parts
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


def deck_height_at(x, z, ramps, flat_decks):
    """Walkable plank height at (x, z): highest of any ramp (linear y over its rect along an axis)
    or flat deck rect under the point, else None. Pure -> unit-testable without a GL context."""
    y = None
    for (x0, z0, x1, z1, y_lo, y_hi, axis) in ramps:
        if x0 <= x <= x1 and z0 <= z <= z1:
            if axis == 'z':
                t = (z - z0) / (z1 - z0) if z1 > z0 else 0.0
            else:
                t = (x - x0) / (x1 - x0) if x1 > x0 else 0.0
            ry = y_lo + (y_hi - y_lo) * t
            y = ry if y is None else max(y, ry)
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
