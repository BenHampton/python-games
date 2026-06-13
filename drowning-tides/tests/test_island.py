import math

from pyglm import glm

from drowning_tides.world.island import resolve_collision


class _Isle:
    def __init__(self, pos, radius):
        self.position = glm.vec3(*pos)
        self.radius = radius


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
