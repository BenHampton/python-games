"""Generate the archipelago: one unique seeded low-poly island per cfg.ISLANDS placement,
each at two LOD levels, into src/drowning_tides/assets/models/islands/<name>_lod{0,1}.glb.

Each island is built procedurally from a noisy surface-of-revolution terrain (sand/rock/grass
bands), with scattered trees/palms, offshore rock spires, and a dock on the home island. LOD1
is the terrain silhouette only (coarser, no props). Colours are baked as glTF vertex colours
(COLOR_0), read by core/model.py. Re-run after tweaking cfg.ISLANDS or the tuning below:

    uv run python tools/gen_islands.py
"""
import math
import random
import sys
from pathlib import Path

import numpy as np
import pygltflib as g
from pygltflib import (
    GLTF2,
    Accessor,
    Attributes,
    Buffer,
    BufferView,
    Mesh,
    Node,
    Primitive,
    Scene,
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from drowning_tides.config import settings as cfg  # noqa: E402
from drowning_tides.core.model import MODELS_DIR, load_vertices  # noqa: E402

OUT_DIR = Path(__file__).resolve().parent.parent / "src/drowning_tides/assets/models/islands"

# muted, cold maritime palette tuned toward DREDGE (low saturation, mossy/slate)
SAND = (0.54, 0.49, 0.38)
ROCK = (0.25, 0.27, 0.28)
ROCK_DARK = (0.16, 0.18, 0.20)
GRASS = (0.18, 0.28, 0.17)
TRUNK = (0.18, 0.13, 0.09)
FOLIAGE = (0.14, 0.26, 0.16)
PALM = (0.18, 0.33, 0.20)
DOCK = (0.30, 0.21, 0.13)
REEF = (0.19, 0.23, 0.24)
HOME_SAND = (0.66, 0.60, 0.46)     # home beach
HOME_DIRT = (0.40, 0.33, 0.23)     # home path
HOME_PATH_HALF = 0.06              # path half-width (model space) along the -z dock corridor

# CC0 Kenney Nature Kit props baked into the islands (with procedural fallback if missing)
NATURE_DIR = MODELS_DIR / "nature"
TREE_MODELS = ['tree_pineDefaultA.glb', 'tree_pineDefaultB.glb', 'tree_pineRoundA.glb',
               'tree_pineRoundB.glb', 'tree_default.glb', 'tree_detailed.glb']
ROCK_MODELS = ['rock_smallA.glb', 'rock_smallB.glb', 'rock_smallC.glb', 'rock_smallD.glb']
BIG_ROCK_MODELS = ['rock_largeA.glb', 'rock_largeB.glb', 'rock_largeC.glb',
                   'rock_tallC.glb', 'rock_tallE.glb']
BUSH_MODELS = ['plant_bush.glb', 'plant_bushDetailed.glb', 'plant_bushLarge.glb',
               'plant_bushSmall.glb']
FLOWER_MODELS = ['flower_redA.glb', 'flower_purpleA.glb', 'flower_yellowA.glb']
GRASS_MODELS = ['grass.glb', 'grass_large.glb', 'grass_leafs.glb']
_ALL_PROPS = TREE_MODELS + ROCK_MODELS + BIG_ROCK_MODELS
PROPS_AVAILABLE = all((NATURE_DIR / m).exists() for m in _ALL_PROPS)
GROUNDCOVER_OK = all((NATURE_DIR / m).exists() for m in BUSH_MODELS + FLOWER_MODELS + GRASS_MODELS)
PROP_MUTE = 0.35            # desaturate Kenney's bright palette toward our muted mood
_PROP_CACHE = {}


def _prop(name):
    """Load a nature glb -> (pos, nrm, col, height), centred on XZ with its base at y=0."""
    if name not in _PROP_CACHE:
        v = load_vertices(NATURE_DIR / name).reshape(-1, 9)
        pos = v[:, :3].copy()
        pos[:, 0] -= (pos[:, 0].min() + pos[:, 0].max()) * 0.5
        pos[:, 2] -= (pos[:, 2].min() + pos[:, 2].max()) * 0.5
        pos[:, 1] -= pos[:, 1].min()
        height = float(pos[:, 1].max()) or 1.0
        _PROP_CACHE[name] = (pos, v[:, 3:6].copy(), v[:, 6:9].copy(), height)
    return _PROP_CACHE[name]


def _norm(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    n = np.cross(b - a, c - a)
    ln = np.linalg.norm(n)
    return (n / ln) if ln > 1e-9 else np.array([0.0, 1.0, 0.0])


def _fbm(x, z, phases):
    """Cheap seeded multi-octave value noise (summed sines) for terrain displacement."""
    v, amp, freq = 0.0, 1.0, 1.0
    for i in range(3):
        v += amp * math.sin(x * freq + phases[i]) * math.cos(z * freq * 1.3 + phases[i + 1])
        amp *= 0.5
        freq *= 2.1
    return v


class Acc:
    """Accumulates flat-shaded, per-vertex-coloured triangles."""

    def __init__(self):
        self.pos, self.nrm, self.col = [], [], []

    def tri(self, a, b, c, color, normal=None):
        n = _norm(a, b, c) if normal is None else np.asarray(normal, dtype=float)
        for p in (a, b, c):
            self.pos.append(p)
            self.nrm.append(n)
            self.col.append(color)

    def quad(self, a, b, c, d, color, normal=None):
        self.tri(a, b, c, color, normal)
        self.tri(a, c, d, color, normal)

    def add_transformed(self, pos, nrm, col, scale, yaw, tx, ty, tz, mute=0.0):
        """Append a prop's triangles, Y-rotated + uniformly scaled + translated into place."""
        ca, sa = math.cos(yaw), math.sin(yaw)
        rot = np.array([[ca, 0.0, sa], [0.0, 1.0, 0.0], [-sa, 0.0, ca]])
        p = pos @ rot.T * scale + np.array([tx, ty, tz])
        n = nrm @ rot.T
        c = col
        if mute:
            lum = (c @ np.array([0.299, 0.587, 0.114]))[:, None]
            c = (c * (1.0 - mute) + lum * mute) * 0.92
        self.pos.extend(map(tuple, p))
        self.nrm.extend(map(tuple, n))
        self.col.extend(map(tuple, c))

    def arrays(self):
        pos = np.array(self.pos, dtype="float32")
        nrm = np.array(self.nrm, dtype="float32")
        col = np.array(self.col, dtype="float32")
        rgba = np.ones((len(col), 4), dtype="float32")
        rgba[:, :3] = col
        return pos, nrm, rgba


# ------------------------------------------------------------------------- terrain
def _profile(kind):
    if kind == "reef":
        return [(1.00, -0.05), (0.90, -0.01), (0.60, 0.03), (0.30, 0.06)], 0.09
    if kind == "home":
        # flat shelf then a short beach; many flat rings so the hill/mountain relief added in
        # _terrain has vertices to shape (the town strip is masked flat). Sync HOME_LAND_FRAC.
        return [(1.00, -0.02), (0.92, 0.00), (0.84, 0.03), (0.74, 0.03), (0.64, 0.03),
                (0.54, 0.03), (0.44, 0.03), (0.34, 0.03), (0.24, 0.03), (0.14, 0.03),
                (0.06, 0.03)], 0.03
    # flatter, less conical: wider mid terraces, a low rounded top
    return [(1.00, -0.06), (0.96, 0.03), (0.82, 0.13), (0.62, 0.27),
            (0.42, 0.40), (0.26, 0.48)], 0.55


def _terrain(acc, rng, kind, seg, lod):
    prof, apex_h = _profile(kind)
    peak = 1.0 if kind in ("reef", "home") else rng.uniform(0.75, 1.15)
    aspect = (rng.uniform(0.72, 1.3), rng.uniform(0.72, 1.3))
    phases = [rng.uniform(0, math.tau) for _ in range(7)]
    hfreq = rng.uniform(2.0, 3.3)
    hamp = {"reef": 0.02, "home": 0.0}.get(kind, 0.105)     # bumpiness (home: dead-flat shelf)
    # the home island is the harbor: keep it a clean circle so the south shore is symmetric
    # about its centre (otherwise a jagged/elongated coast skews the dock + stairs off-centre)
    home = kind == "home"
    if home:
        aspect = (1.0, 1.0)

    def rmul(ang):
        if home:
            return 1.0
        # jagged coastline: more + higher-frequency radial variation
        return (1.0 + 0.26 * math.sin(ang * 3 + phases[0])
                + 0.16 * math.sin(ang * 5 + phases[1])
                + 0.11 * math.sin(ang * 8 + phases[2])
                + 0.06 * math.sin(ang * 13 + phases[3]))

    def home_relief(x, z, rf):
        # home island: a central mountain + rolling hills everywhere EXCEPT the flat harbor town
        # strip, faded out near the coast so the beach/waterline stays clean.
        if not home:
            return 0.0
        mountain = max(0.0, 0.52 - rf) * 0.70           # central peak, gone beyond r~0.52
        hills = _fbm(x * 3.0, z * 3.0, phases) * 0.06    # rolling hills
        coast = min(1.0, max(0.0, (0.86 - rf) / 0.18))   # keep the coast/beach clean
        keep = max(abs(x) - 0.36, z + 0.30)              # <=0 over the flat town strip
        tmask = 0.0 if keep <= 0.0 else min(1.0, keep / 0.16)
        return (mountain + hills) * coast * tmask

    n_ring = len(prof)
    rings = []
    for k, (rf, h) in enumerate(prof):
        t = k / (n_ring - 1)
        band = 4.0 * t * (1.0 - t)          # 0 at base/apex, 1 mid -> cliffs bump most
        verts = []
        for s in range(seg):
            ang = math.tau * s / seg
            r = rf * rmul(ang)
            x = r * math.cos(ang) * aspect[0]
            z = r * math.sin(ang) * aspect[1]
            y = (h * peak + _fbm(x * hfreq, z * hfreq, phases) * hamp * (0.4 + 0.6 * band)
                 + home_relief(x, z, rf))
            verts.append((x, y, z))
        rings.append(verts)
    apex = (rng.uniform(-0.04, 0.04), apex_h * peak, rng.uniform(-0.04, 0.04))
    apex = (apex[0], apex[1] + home_relief(apex[0], apex[2], 0.0), apex[2])
    peak_y = apex[1]

    def color(cx, cy, cz, ny):
        if kind == "home":
            if cy < 0.02:
                return HOME_SAND                         # lower beach
            if cy > 0.18:
                return ROCK                              # rocky mountain upper slopes
            return GRASS                                 # forested shelf + hills
        if kind == "reef":
            return SAND if cy < 0.0 else REEF
        if ny < 0.5:
            return ROCK if cy > 0.18 else ROCK_DARK
        if cy < 0.06:
            return SAND
        if cy < 0.32 * peak_y:
            return ROCK
        return GRASS

    def face(a, b, c):
        n = _norm(a, b, c)
        if n[1] < 0:
            n = -n
        cx = (a[0] + b[0] + c[0]) / 3.0
        cy = (a[1] + b[1] + c[1]) / 3.0
        cz = (a[2] + b[2] + c[2]) / 3.0
        acc.tri(a, b, c, color(cx, cy, cz, n[1]), n)

    for k in range(len(rings) - 1):
        lo, hi = rings[k], rings[k + 1]
        for s in range(seg):
            s2 = (s + 1) % seg
            face(lo[s], lo[s2], hi[s2])
            face(lo[s], hi[s2], hi[s])
    top = rings[-1]
    for s in range(seg):
        face(top[s], top[(s + 1) % seg], apex)

    # base cap (underside, faces down)
    base = rings[0]
    center = (0.0, prof[0][1] * peak - 0.04, 0.0)
    for s in range(seg):
        acc.tri(base[(s + 1) % seg], base[s], center, ROCK_DARK, (0, -1, 0))

    # candidates for trees/rocks: all land verts (home: shelf + hills), else high ground
    thr = 0.01 if home else 0.30 * peak_y
    grass = [v for ring in rings for v in ring if v[1] > thr]

    def height_at(x, z):
        # model surface height at (x, z) — used so scattered foliage/rocks sit on the terrain
        # instead of floating (exact for the home island: rmul=1, aspect=1, hamp=0).
        r = math.hypot(x, z)
        if r >= prof[0][0]:
            h = prof[0][1]
        elif r <= prof[-1][0]:
            h = prof[-1][1]
        else:
            h = prof[-1][1]
            for (r0, h0), (r1, h1) in zip(prof, prof[1:], strict=False):
                if r1 <= r <= r0:
                    h = h1 + (h0 - h1) * (r - r1) / (r0 - r1)
                    break
        return h * peak + home_relief(x, z, r)

    return grass, peak_y, height_at


# ----------------------------------------------------------------------- props
def _cone(acc, cx, cz, base_y, radius, height, color, seg=6):
    apex = (cx, base_y + height, cz)
    ring = [(cx + radius * math.cos(math.tau * i / seg),
             base_y, cz + radius * math.sin(math.tau * i / seg)) for i in range(seg)]
    for i in range(seg):
        a, b = ring[i], ring[(i + 1) % seg]
        n = _norm(a, b, apex)
        if (n[0] * (a[0] - cx) + n[2] * (a[2] - cz)) < 0:
            n = -n
        acc.tri(a, b, apex, color, n)


def _box(acc, cx, cz, y0, y1, half, color):
    xs = (cx - half, cx + half)
    zs = (cz - half, cz + half)
    corners = {
        (0, 0): (xs[0], zs[0]), (1, 0): (xs[1], zs[0]),
        (1, 1): (xs[1], zs[1]), (0, 1): (xs[0], zs[1]),
    }
    loop = [(0, 0), (1, 0), (1, 1), (0, 1)]
    for i in range(4):
        x0, z0 = corners[loop[i]]
        x1, z1 = corners[loop[(i + 1) % 4]]
        acc.quad((x0, y0, z0), (x1, y0, z1), (x1, y1, z1), (x0, y1, z0), color)
    acc.quad((xs[0], y1, zs[0]), (xs[1], y1, zs[0]),
             (xs[1], y1, zs[1]), (xs[0], y1, zs[1]), color, (0, 1, 0))


def _tree(acc, x, z, y, rng, palmy):
    if palmy:
        h = rng.uniform(0.10, 0.16)
        _box(acc, x, z, y, y + h, 0.008, TRUNK)
        for i in range(5):
            ang = math.tau * i / 5 + rng.uniform(-0.2, 0.2)
            tip = (x + 0.09 * math.cos(ang), y + h - 0.02, z + 0.09 * math.sin(ang))
            side = (x + 0.02 * math.cos(ang + 1.2), y + h, z + 0.02 * math.sin(ang + 1.2))
            acc.tri((x, y + h, z), side, tip, PALM)
    else:
        h = rng.uniform(0.05, 0.09)
        _box(acc, x, z, y, y + h, 0.012, TRUNK)
        _cone(acc, x, z, y + h * 0.7, rng.uniform(0.05, 0.08), rng.uniform(0.09, 0.14), FOLIAGE)


def _add_trees(acc, rng, grass, palmy):
    if not grass:
        return
    if not PROPS_AVAILABLE:
        return _add_trees_procedural(acc, rng, grass, palmy)
    for _ in range(rng.randint(10, 22)):
        v = rng.choice(grass)
        pos, nrm, col, h = _prop(rng.choice(TREE_MODELS))
        target = rng.uniform(0.10, 0.17)
        acc.add_transformed(pos, nrm, col, target / h, rng.uniform(0.0, math.tau),
                            v[0] + rng.uniform(-0.03, 0.03), v[1] - 0.01,
                            v[2] + rng.uniform(-0.03, 0.03), mute=PROP_MUTE)


def _add_rocks(acc, rng, grass):
    """Scatter small rocks over the island for ground detail."""
    if not grass:
        return
    if not PROPS_AVAILABLE:
        return _add_rocks_procedural(acc, rng, grass)
    for _ in range(rng.randint(10, 20)):
        v = rng.choice(grass)
        pos, nrm, col, h = _prop(rng.choice(ROCK_MODELS))
        target = rng.uniform(0.04, 0.09)
        acc.add_transformed(pos, nrm, col, target / h, rng.uniform(0.0, math.tau),
                            v[0] + rng.uniform(-0.05, 0.05), v[1] - 0.02,
                            v[2] + rng.uniform(-0.05, 0.05), mute=PROP_MUTE)


def _add_offshore_rocks(acc, rng):
    """Large rock formations around the shoreline (replaces the procedural spires)."""
    if not PROPS_AVAILABLE:
        return _add_spires_procedural(acc, rng)
    for _ in range(rng.randint(3, 6)):
        ang = rng.uniform(0.0, math.tau)
        r = rng.uniform(0.9, 1.4)
        pos, nrm, col, h = _prop(rng.choice(BIG_ROCK_MODELS))
        target = rng.uniform(0.22, 0.55)
        acc.add_transformed(pos, nrm, col, target / h, rng.uniform(0.0, math.tau),
                            r * math.cos(ang), -0.05, r * math.sin(ang), mute=PROP_MUTE)


def _add_trees_procedural(acc, rng, grass, palmy):
    for _ in range(rng.randint(8, 18)):
        v = rng.choice(grass)
        _tree(acc, v[0] + rng.uniform(-0.03, 0.03), v[2] + rng.uniform(-0.03, 0.03),
              v[1] - 0.01, rng, palmy)


def _add_rocks_procedural(acc, rng, grass):
    for _ in range(rng.randint(8, 16)):
        v = rng.choice(grass)
        r = rng.uniform(0.03, 0.07)
        _cone(acc, v[0] + rng.uniform(-0.05, 0.05), v[2] + rng.uniform(-0.05, 0.05),
              v[1] - 0.02, r, rng.uniform(0.02, 0.05), ROCK if rng.random() < 0.5 else ROCK_DARK)


def _add_spires_procedural(acc, rng):
    for _ in range(rng.randint(3, 6)):
        ang = rng.uniform(0, math.tau)
        r = rng.uniform(0.95, 1.35)
        cx, cz = r * math.cos(ang), r * math.sin(ang)
        top = rng.uniform(0.18, 0.5)
        half = rng.uniform(0.05, 0.1)
        for i in range(4):
            a0 = math.tau * i / 4
            a1 = math.tau * (i + 1) / 4
            b0 = (cx + half * math.cos(a0), -0.05, cz + half * math.sin(a0))
            b1 = (cx + half * math.cos(a1), -0.05, cz + half * math.sin(a1))
            t0 = (cx + half * 0.3 * math.cos(a0), top, cz + half * 0.3 * math.sin(a0))
            t1 = (cx + half * 0.3 * math.cos(a1), top, cz + half * 0.3 * math.sin(a1))
            acc.quad(b0, b1, t1, t0, ROCK)


def _add_dock(acc, rng):
    ang = rng.uniform(0, math.tau)
    dx, dz = math.cos(ang), math.sin(ang)
    px, pz = -dz, dx          # perpendicular (plank width axis)
    w = 0.07
    r0, r1, y = 0.6, 1.25, 0.04
    a = (dx * r0 + px * w, y, dz * r0 + pz * w)
    b = (dx * r0 - px * w, y, dz * r0 - pz * w)
    c = (dx * r1 - px * w, y, dz * r1 - pz * w)
    d = (dx * r1 + px * w, y, dz * r1 + pz * w)
    acc.quad(a, b, c, d, DOCK, (0, 1, 0))
    # stilts
    for (sx, sz) in ((dx * r1, dz * r1), (dx * (r0 + r1) * 0.5, dz * (r0 + r1) * 0.5)):
        _box(acc, sx, sz, -0.08, y, 0.02, DOCK)


# ----------------------------------------------------------------- home foliage detail
def _add_trees_clustered(acc, rng, grass, palmy, scale, height_at):
    """Trees in clumps (a forest); world-sized and seated on the terrain via height_at so they
    don't float over the hills."""
    if not (grass and PROPS_AVAILABLE):
        return _add_trees(acc, rng, grass, palmy)
    spread = 13.0 / scale
    for _ in range(rng.randint(16, 24)):                 # a forest over the rest of the island
        cv = rng.choice(grass)
        for _ in range(rng.randint(3, 5)):
            pos, nrm, col, h = _prop(rng.choice(TREE_MODELS))
            target = rng.uniform(5.5, 9.0) / scale
            fx = cv[0] + rng.uniform(-spread, spread)
            fz = cv[2] + rng.uniform(-spread, spread)
            acc.add_transformed(pos, nrm, col, target / h, rng.uniform(0.0, math.tau),
                                fx, height_at(fx, fz) - 0.02, fz, mute=PROP_MUTE)


def _add_groundcover(acc, rng, grass, scale, height_at):
    """Scatter bushes, flowers and grass tufts (CC0 Nature Kit), world-sized, seated on terrain."""
    if not (grass and GROUNDCOVER_OK):
        return
    jit = 7.0 / scale
    for models, count, lo, hi in (
        (BUSH_MODELS, rng.randint(16, 26), 1.4, 2.8),
        (FLOWER_MODELS, rng.randint(28, 44), 0.5, 1.1),
        (GRASS_MODELS, rng.randint(36, 56), 0.5, 1.3),
    ):
        for _ in range(count):
            v = rng.choice(grass)
            pos, nrm, col, h = _prop(rng.choice(models))
            target = rng.uniform(lo, hi) / scale
            fx = v[0] + rng.uniform(-jit, jit)
            fz = v[2] + rng.uniform(-jit, jit)
            acc.add_transformed(pos, nrm, col, target / h, rng.uniform(0.0, math.tau),
                                fx, height_at(fx, fz) - 0.01, fz, mute=PROP_MUTE)


# --------------------------------------------------------------------- heightfield
def _bake_heightmap(verts, grid=256):
    """Rasterize terrain triangles (model space) into a (grid, grid) top-surface heightmap.
    heights[j, i] is the max surface y over cell (i<->x, j<->z); `ext` is the model half-extent
    so the grid spans [-ext, ext]^2. Used by Island.ground_y so the player follows the real
    surface. Pass terrain-only triangles (no foliage)."""
    v = np.asarray(verts, dtype=float)
    tris = v.reshape(-1, 3, 3)
    ext = float(np.abs(v[:, [0, 2]]).max()) * 1.02
    cell = 2.0 * ext / grid
    heights = np.full((grid, grid), -1e30)
    for t in tris:
        x, y, z = t[:, 0], t[:, 1], t[:, 2]
        i0 = max(int((x.min() + ext) / cell), 0)
        i1 = min(int((x.max() + ext) / cell) + 1, grid - 1)
        j0 = max(int((z.min() + ext) / cell), 0)
        j1 = min(int((z.max() + ext) / cell) + 1, grid - 1)
        if i1 < i0 or j1 < j0:
            continue
        x0, x1, x2 = x
        z0, z1, z2 = z
        denom = (z1 - z2) * (x0 - x2) + (x2 - x1) * (z0 - z2)
        if abs(denom) < 1e-15:
            continue
        px = -ext + (np.arange(i0, i1 + 1) + 0.5) * cell
        pz = -ext + (np.arange(j0, j1 + 1) + 0.5) * cell
        gx, gz = np.meshgrid(px, pz)
        a = ((z1 - z2) * (gx - x2) + (x2 - x1) * (gz - z2)) / denom
        b = ((z2 - z0) * (gx - x2) + (x0 - x2) * (gz - z2)) / denom
        c = 1.0 - a - b
        inside = (a >= -1e-6) & (b >= -1e-6) & (c >= -1e-6)
        yh = a * y[0] + b * y[1] + c * y[2]
        block = heights[j0:j1 + 1, i0:i1 + 1]
        np.maximum(block, np.where(inside, yh, -1e30), out=block)
    touched = heights[heights > -1e29]
    heights[heights <= -1e29] = float(touched.min()) if touched.size else 0.0
    return heights.astype("float32"), ext


def _add_island_rocks(acc, rng, grass, scale, height_at):
    """Boulders + rocks on the home island (world-sized) plus shoreline boulders, all seated on the
    terrain; skips the south harbor sector so the dock stays clear."""
    if not (grass and PROPS_AVAILABLE):
        return
    for _ in range(rng.randint(24, 36)):                 # rocks/boulders on the land + hills
        v = rng.choice(grass)
        big = rng.random() < 0.45
        pos, nrm, col, h = _prop(rng.choice(BIG_ROCK_MODELS if big else ROCK_MODELS))
        target = (rng.uniform(3.5, 8.0) if big else rng.uniform(1.0, 2.5)) / scale
        fx = v[0] + rng.uniform(-0.03, 0.03)
        fz = v[2] + rng.uniform(-0.03, 0.03)
        acc.add_transformed(pos, nrm, col, target / h, rng.uniform(0.0, math.tau),
                            fx, height_at(fx, fz) - 0.05, fz, mute=PROP_MUTE)
    for _ in range(rng.randint(10, 16)):                 # shoreline boulders (not in the harbor)
        ang = rng.uniform(0.0, math.tau)
        cxr, czr = math.cos(ang), math.sin(ang)
        if czr < -0.3 and abs(cxr) < 0.5:
            continue
        rr = rng.uniform(0.86, 0.98)
        fx, fz = rr * cxr, rr * czr
        pos, nrm, col, h = _prop(rng.choice(BIG_ROCK_MODELS))
        target = rng.uniform(4.0, 9.0) / scale
        acc.add_transformed(pos, nrm, col, target / h, rng.uniform(0.0, math.tau),
                            fx, height_at(fx, fz) - 0.1, fz, mute=PROP_MUTE)


# ------------------------------------------------------------------------- glb io
def gen_island(spec, lod):
    rng = random.Random(spec["seed"] * 100 + lod)
    acc = Acc()
    seg = (36 if spec["kind"] == "home" else 20) if lod == 0 else 10
    grass, _, height_at = _terrain(acc, rng, spec["kind"], seg, lod)
    heightmap = _bake_heightmap(acc.pos) if lod == 0 else None   # terrain-only (pre-foliage)
    if lod == 0 and spec["kind"] != "reef":
        palmy = spec["seed"] % 2 == 0
        if spec["kind"] == "home":
            # forest the island, but keep foliage OUT of the harbor town (south-central strip,
            # model space: |x|<0.36 and z<-0.30) so the buildings/docks read cleanly
            grass = [v for v in grass if not (v[2] < -0.30 and abs(v[0]) < 0.36)]
            _add_trees_clustered(acc, rng, grass, palmy, spec["scale"], height_at)
            _add_groundcover(acc, rng, grass, spec["scale"], height_at)
            _add_island_rocks(acc, rng, grass, spec["scale"], height_at)
        else:
            _add_trees(acc, rng, grass, palmy)
            _add_rocks(acc, rng, grass)
            _add_offshore_rocks(acc, rng)
    return acc.arrays(), heightmap


def write_glb(path, pos, nrm, rgba):
    blob = pos.tobytes() + nrm.tobytes() + rgba.tobytes()
    off_n = pos.nbytes
    off_c = pos.nbytes + nrm.nbytes
    gltf = GLTF2(
        scenes=[Scene(nodes=[0])],
        nodes=[Node(mesh=0)],
        meshes=[Mesh(primitives=[
            Primitive(attributes=Attributes(POSITION=0, NORMAL=1, COLOR_0=2))
        ])],
        accessors=[
            Accessor(bufferView=0, componentType=g.FLOAT, count=len(pos), type="VEC3",
                     min=pos.min(0).tolist(), max=pos.max(0).tolist()),
            Accessor(bufferView=1, componentType=g.FLOAT, count=len(nrm), type="VEC3"),
            Accessor(bufferView=2, componentType=g.FLOAT, count=len(rgba), type="VEC4"),
        ],
        bufferViews=[
            BufferView(buffer=0, byteOffset=0, byteLength=pos.nbytes, target=g.ARRAY_BUFFER),
            BufferView(buffer=0, byteOffset=off_n, byteLength=nrm.nbytes, target=g.ARRAY_BUFFER),
            BufferView(buffer=0, byteOffset=off_c, byteLength=rgba.nbytes, target=g.ARRAY_BUFFER),
        ],
        buffers=[Buffer(byteLength=len(blob))],
    )
    gltf.set_binary_blob(blob)
    gltf.save_binary(str(path))


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for spec in cfg.ISLANDS:
        tris = {}
        for lod in (0, 1):
            (pos, nrm, rgba), heightmap = gen_island(spec, lod)
            write_glb(OUT_DIR / f"{spec['name']}_lod{lod}.glb", pos, nrm, rgba)
            tris[lod] = len(pos) // 3
            if heightmap is not None:
                heights, ext = heightmap
                np.savez(OUT_DIR / f"{spec['name']}_height.npz", heights=heights, ext=ext)
        print(f"{spec['name']:16s} {spec['kind']:7s} lod0={tris[0]:4d} lod1={tris[1]:4d} tris")
    print(f"wrote {len(cfg.ISLANDS) * 2} glbs + {len(cfg.ISLANDS)} heightmaps to {OUT_DIR}")


if __name__ == "__main__":
    main()
