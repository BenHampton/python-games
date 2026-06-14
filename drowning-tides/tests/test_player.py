import math

from pyglm import glm

from drowning_tides.world.player import walk

CENTER = glm.vec2(0.0, 0.0)


def test_walk_forward_along_yaw_and_pins_height():
    # yaw=0 -> forward = (sin0, cos0) = +z
    p = walk(glm.vec3(0, 9, 0), 0.0, 1.0, 0.0, 0.5, CENTER, 100.0, 3.0, 9.0)
    assert p.z > 0 and abs(p.x) < 1e-6
    assert abs(p.y - 3.0) < 1e-9          # y pinned to land_y


def test_walk_strafe_goes_right():
    p = walk(glm.vec3(0, 3, 0), 0.0, 0.0, 1.0, 0.5, CENTER, 100.0, 3.0, 9.0)
    assert p.x > 0 and abs(p.z) < 1e-6


def test_walk_clamped_to_island_disc():
    # forward = +x (yaw = pi/2); walk far outward -> clamped to the radius
    p = walk(glm.vec3(8, 3, 0), math.pi / 2, 1.0, 0.0, 1.0, CENTER, 10.0, 3.0, 9.0)
    assert abs(math.hypot(p.x, p.z) - 10.0) < 1e-4


def test_walk_no_input_holds_position():
    p = walk(glm.vec3(4, 0, -3), 1.2, 0.0, 0.0, 0.5, CENTER, 100.0, 2.0, 9.0)
    assert abs(p.x - 4) < 1e-6 and abs(p.z + 3) < 1e-6 and abs(p.y - 2.0) < 1e-9
