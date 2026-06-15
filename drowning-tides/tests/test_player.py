import math

from pyglm import glm

from drowning_tides.world.player import disembark_pos, walk
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


# walkable docks: ramps (x0,z0,x1,z1, y_lo, y_hi, axis) + flat deck rects (x0,z0,x1,z1, y)
# a z-axis ramp: at z-min(-20) the deck is 0.6, at z-max(-10) it's 3.0
RAMPS = [(-1.6, -20.0, 1.6, -10.0, 0.6, 3.0, 'z')]
DECKS = [(5.0, -25.0, 9.0, -21.0, 0.6)]


def test_deck_height_ramp_slopes_along_axis():
    assert math.isclose(deck_height_at(0, -10, RAMPS, []), 3.0)        # z-max end
    assert math.isclose(deck_height_at(0, -20, RAMPS, []), 0.6)        # z-min end
    assert math.isclose(deck_height_at(0, -15, RAMPS, []), 1.8)        # midpoint


def test_deck_height_flat_rect_and_off():
    assert math.isclose(deck_height_at(7, -23, [], DECKS), 0.6)        # on the flat rect
    assert deck_height_at(50, 50, RAMPS, DECKS) is None                # open water


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


def test_boat_stopped_at_dock_face():
    # T-head crossbar footprint; a boat disc (r2) approaching from the south is pushed back so it
    # moors just off the face rather than sailing through the planks
    thead = [(-7.0, -286.7, 7.0, -282.7)]
    x, z = resolve_town_collision(0.0, -288.0, thead, 2.0)
    assert math.isclose(z, -288.7, abs_tol=1e-6) and math.isclose(x, 0.0, abs_tol=1e-6)


def test_disembark_pos_is_offset_toward_center():
    # boat south of the island centre -> land just inland (north) of the boat, beside it
    item = glm.vec2(0.0, -288.0)
    center = glm.vec2(0.0, -185.0)
    place, inland = disembark_pos(item, center, 3.5)
    assert math.isclose(glm.length(place - item), 3.5, abs_tol=1e-5)   # exactly the offset away
    assert place.y > item.y and abs(place.x) < 1e-6                    # toward the centre (+z)
    assert math.isclose(inland.x, 0.0, abs_tol=1e-6) and inland.y > 0  # unit inland direction
