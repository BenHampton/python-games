"""Islands: unique seeded low-poly glTF models placed per cfg.ISLANDS, with frustum +
distance culling, distance LOD, and simple disc collision.

Geometry is baked by `tools/gen_islands.py` (two LOD levels per island) and loaded through
`core/model.py::Model`. `IslandField` owns the archipelago and, each frame, skips islands
outside the frustum or beyond the cull distance and picks an LOD by distance.
"""
import math

from pyglm import glm

from drowning_tides.config import settings as cfg
from drowning_tides.core.frustum import extract_planes, sphere_visible
from drowning_tides.core.model import MODELS_DIR, Model

ISLANDS_DIR = MODELS_DIR / "islands"


class Island:
    def __init__(self, app, spec):
        self.name = spec["name"]
        self.position = glm.vec3(*spec["pos"])
        self.radius = spec["radius"]          # collision disc
        scale, yaw = spec["scale"], spec["yaw"]
        self.kind = spec["kind"]
        self.dockable = spec["kind"] != "reef"        # can't disembark onto a reef
        if self.kind == "home":                       # big flat island
            self.land_y = scale * cfg.HOME_LAND_FRAC
            self.walk_frac = cfg.HOME_WALK_FRAC
            self.spawn_frac = cfg.HOME_SPAWN_FRAC
        else:                                          # mesa: walk the summit
            self.land_y = scale * cfg.ISLAND_LAND_FRAC
            self.walk_frac = cfg.ISLAND_WALK_FRAC
            self.spawn_frac = cfg.ISLAND_SPAWN_FRAC

        self.lods = [
            Model(app.ctx, app.shader_program.model, ISLANDS_DIR / f"{self.name}_lod{lod}.glb",
                  position=spec["pos"], scale=scale, yaw=yaw)
            for lod in (0, 1)
        ]

        # world-space bounding sphere from LOD0 (for culling)
        m = self.lods[0].m_model
        self.center = glm.vec3(m * glm.vec4(self.lods[0].local_center, 1.0))
        self.cull_radius = self.lods[0].local_radius * scale

    def ground_y(self, x, z):
        """Walkable ground height at (x, z). The home island ramps from the shore up to its
        flat plateau so you can walk up the beach; other islands use a flat summit plane."""
        if self.kind != 'home':
            return self.land_y
        r = math.hypot(x - self.position.x, z - self.position.z) / self.radius
        if r <= cfg.HOME_FLAT_FRAC:
            return self.land_y
        if r >= 1.0:
            return cfg.HOME_SHORE_Y
        t = (r - cfg.HOME_FLAT_FRAC) / (1.0 - cfg.HOME_FLAT_FRAC)
        return self.land_y * (1.0 - t) + cfg.HOME_SHORE_Y * t

    def render(self, lod):
        self.lods[lod].render()


class IslandField:
    def __init__(self, app):
        self.app = app
        self.islands = [Island(app, spec) for spec in cfg.ISLANDS]

    def render(self, camera):
        planes = extract_planes(camera.m_proj * camera.m_view)
        cam = camera.position
        for isl in self.islands:
            dist = glm.length(cam - isl.center)
            if dist - isl.cull_radius > cfg.ISLAND_CULL_DIST:
                continue
            if not sphere_visible(planes, isl.center, isl.cull_radius):
                continue
            isl.render(0 if dist < cfg.ISLAND_LOD_DIST else 1)

    def collide(self, x, z, boat_radius):
        return resolve_collision(x, z, self.islands, boat_radius)

    def nearest_dockable(self, pos):
        """Nearest dockable island whose shore is within cfg.DOCK_RANGE of pos, else None."""
        best, best_d = None, cfg.DOCK_RANGE
        for isl in self.islands:
            if not isl.dockable:
                continue
            d = math.hypot(pos.x - isl.position.x, pos.z - isl.position.z) - isl.radius
            if d < best_d:
                best, best_d = isl, d
        return best


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
