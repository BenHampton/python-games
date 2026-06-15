import math

from pyglm import glm

from drowning_tides.world.player import walk
from drowning_tides.world.town import deck_height_at, resolve_town_collision

CENTER = glm.vec2(0.0, 0.0)
BOX = [(-2.0, -2.0, 2.0, 2.0)]   # a solid footprint centred at origin


def test_collision_pushes_out_when_inside():
    # standing inside the box -> ejected to the nearest face (+x here) plus radius
    x, z = resolve_town_collision(1.5, 0.0, BOX, 0.5)
    assert math.isclose(x, 2.5, abs_tol=1e-6) and math.isclose(z, 0.0, abs_tol=1e-6)


def test_collision_pushes_off_a_face():
    # just outside the +x face but within radius -> pushed back to face + radius
    x, z = resolve_town_collision(2.3, 0.0, BOX, 0.5)
    assert math.isclose(x, 2.5, abs_tol=1e-6) and math.isclose(z, 0.0, abs_tol=1e-6)


def test_collision_leaves_clear_point_untouched():
    x, z = resolve_town_collision(5.0, 5.0, BOX, 0.5)
    assert (x, z) == (5.0, 5.0)


# walkable docks: sloped pier (cx, hw, z_far, z_near) + flat deck rects
PIER = (0.0, 1.6, -20.0, -10.0)
DECKS = [(5.0, -25.0, 9.0, -21.0, 0.6)]


def test_deck_height_pier_slopes_land_to_deck():
    assert math.isclose(deck_height_at(0, -10, PIER, [], 3.0, 0.6), 3.0)        # near = land
    assert math.isclose(deck_height_at(0, -20, PIER, [], 3.0, 0.6), 0.6)        # far = deck top
    assert math.isclose(deck_height_at(0, -15, PIER, [], 3.0, 0.6), 1.8)        # midpoint


def test_deck_height_flat_rect_and_off():
    assert math.isclose(deck_height_at(7, -23, None, DECKS, 3.0, 0.6), 0.6)     # on the rect
    assert deck_height_at(50, 50, PIER, DECKS, 3.0, 0.6) is None                # open water


def test_walk_forward_along_yaw_and_pins_height():
    # yaw=0 -> forward = (sin0, cos0) = +z
    p = walk(glm.vec3(0, 9, 0), 0.0, 1.0, 0.0, 0.5, CENTER, 100.0, 3.0, 9.0)
    assert p.z > 0 and abs(p.x) < 1e-6
    assert abs(p.y - 3.0) < 1e-9          # y pinned to land_y


def test_walk_strafe_right_and_left_are_opposite():
    # facing +Z (yaw 0), the player's right (D) is -X and left (A) is +X
    right = walk(glm.vec3(0, 3, 0), 0.0, 0.0, 1.0, 0.5, CENTER, 100.0, 3.0, 9.0)
    left = walk(glm.vec3(0, 3, 0), 0.0, 0.0, -1.0, 0.5, CENTER, 100.0, 3.0, 9.0)
    assert right.x < 0 and abs(right.z) < 1e-6
    assert left.x > 0 and abs(left.z) < 1e-6


def test_walk_clamped_to_island_disc():
    # forward = +x (yaw = pi/2); walk far outward -> clamped to the radius
    p = walk(glm.vec3(8, 3, 0), math.pi / 2, 1.0, 0.0, 1.0, CENTER, 10.0, 3.0, 9.0)
    assert abs(math.hypot(p.x, p.z) - 10.0) < 1e-4


def test_walk_no_input_holds_position():
    p = walk(glm.vec3(4, 0, -3), 1.2, 0.0, 0.0, 0.5, CENTER, 100.0, 2.0, 9.0)
    assert abs(p.x - 4) < 1e-6 and abs(p.z + 3) < 1e-6 and abs(p.y - 2.0) < 1e-9
