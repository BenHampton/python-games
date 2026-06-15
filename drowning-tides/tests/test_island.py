import math

import numpy as np
from pyglm import glm

from drowning_tides.config import settings as cfg
from drowning_tides.world.island import IslandField, resolve_collision, sample_height


class _Isle:
    def __init__(self, pos, radius, dockable=True):
        self.position = glm.vec3(*pos)
        self.radius = radius
        self.dockable = dockable


def _field(islands):
    f = IslandField.__new__(IslandField)   # skip GL-heavy __init__
    f.islands = islands
    return f


ISLANDS = [_Isle((0.0, 0.0, 0.0), 10.0)]
BOAT_R = 2.0


def test_no_collision_when_clear():
    x, z, hit = resolve_collision(50.0, 0.0, ISLANDS, BOAT_R)
    assert not hit
    assert (x, z) == (50.0, 0.0)


def test_pushed_to_boundary_when_inside():
    x, z, hit = resolve_collision(3.0, 0.0, ISLANDS, BOAT_R)
    assert hit
    assert math.isclose(math.hypot(x, z), 10.0 + BOAT_R, rel_tol=1e-6)
    assert x > 0 and math.isclose(z, 0.0, abs_tol=1e-6)  # pushed straight out along +x


def test_center_degenerate_pushes_out():
    x, z, hit = resolve_collision(0.0, 0.0, ISLANDS, BOAT_R)
    assert hit
    assert math.isclose(math.hypot(x, z), 10.0 + BOAT_R, rel_tol=1e-6)


def test_nearest_dockable_within_range():
    field = _field([_Isle((0, 0, 0), 10.0), _Isle((300, 0, 0), 10.0)])
    near = field.nearest_dockable(glm.vec3(0, 0, 10.0 + cfg.DOCK_RANGE - 1))  # just inside
    assert near is field.islands[0]


def test_nearest_dockable_none_when_far():
    field = _field([_Isle((0, 0, 0), 10.0)])
    assert field.nearest_dockable(glm.vec3(0, 0, 500)) is None


def test_nearest_dockable_skips_reefs():
    field = _field([_Isle((0, 0, 0), 10.0, dockable=False)])
    assert field.nearest_dockable(glm.vec3(0, 0, 12)) is None


def test_boat_start_clears_island_collision():
    # the moored boat must start outside every island disc (no collision push at spawn)
    discs = [_Isle((s['pos'][0], 0.0, s['pos'][2]), s['radius']) for s in cfg.ISLANDS]
    _, _, hit = resolve_collision(cfg.BOAT_START_POS.x, cfg.BOAT_START_POS.z, discs,
                                  cfg.BOAT_COLLISION_RADIUS)
    assert not hit


# --- heightmap sampling (world->model + bilinear) ----------------------------------
def _ramp_grid(g=4):
    """heights[j, i] = i (depends only on the x index) -> easy to reason about."""
    h = np.zeros((g, g), dtype="float32")
    h[:, :] = np.arange(g)
    return h


# ext=2, g=4 -> cell=1; cell centres in model x are -1.5, -0.5, 0.5, 1.5 (indices 0..3)
def test_sample_height_exact_at_cell_centre():
    y = sample_height(_ramp_grid(), 2.0, 1.0, 0.0, glm.vec3(0, 0, 0), -0.5, -0.5)
    assert math.isclose(y, 1.0, abs_tol=1e-5)         # i=1 -> height 1


def test_sample_height_bilinear_between_cells():
    y = sample_height(_ramp_grid(), 2.0, 1.0, 0.0, glm.vec3(0, 0, 0), 0.0, -0.5)
    assert math.isclose(y, 1.5, abs_tol=1e-5)         # halfway between i=1 (1) and i=2 (2)


def test_sample_height_applies_scale():
    y = sample_height(_ramp_grid(), 2.0, 10.0, 0.0, glm.vec3(0, 0, 0), -5.0, -5.0)
    assert math.isclose(y, 10.0, abs_tol=1e-4)        # world -5 -> model -0.5 (h=1) * scale 10


def test_sample_height_applies_pos_offset():
    y = sample_height(_ramp_grid(), 2.0, 1.0, 0.0, glm.vec3(100, 5, -50), 99.5, -50.5)
    assert math.isclose(y, 6.0, abs_tol=1e-5)         # pos.y(5) + h(1)*scale(1)


def test_sample_height_honors_yaw():
    h, pos = _ramp_grid(), glm.vec3(0, 0, 0)
    # yaw rotates world->model, so the same point samples a different column than yaw=0
    assert math.isclose(sample_height(h, 2.0, 1.0, 0.0, pos, 1.5, 0.5), 3.0, abs_tol=1e-5)
    assert math.isclose(sample_height(h, 2.0, 1.0, math.pi / 2, pos, 1.5, 0.5), 1.0, abs_tol=1e-5)
