import math

from pyglm import glm

from drowning_tides.config import settings as cfg
from drowning_tides.render.camera import FIRST_PERSON, Camera


class _Boat:
    def __init__(self):
        self.position = glm.vec3(0.0, 0.0, 0.0)
        self.forward = glm.vec3(0.0, 0.0, 1.0)
        self.yaw = 0.0


class _Player:
    def __init__(self):
        self.position = glm.vec3(0.0, 0.0, 0.0)


class _App:
    def __init__(self):
        self.boat = _Boat()
        self.player = _Player()


def _camera():
    return Camera(_App())


def test_starts_framed_behind_the_boat():
    cam = _camera()
    # boat faces +Z, so the camera should sit on the -Z side and above the water
    assert cam.position.z < 0.0
    assert cam.position.y > 0.0


def test_add_look_changes_yaw_and_pitch():
    cam = _camera()
    y0, p0 = cam.orbit_yaw, cam.orbit_pitch
    cam.add_look(40.0, 0.0)
    assert math.isclose(cam.orbit_yaw, y0 + 40.0 * cfg.MOUSE_SENSITIVITY)
    assert cam.orbit_pitch == p0
    cam.add_look(0.0, 20.0)
    assert cam.orbit_pitch != p0  # default (non-inverted) Y moves pitch


def test_pitch_moves_opposite_per_mode():
    # same vertical input tilts the view up in both modes -> opposite raw pitch deltas
    follow = Camera(_App())
    fp = Camera(_App(), mode=FIRST_PERSON)
    p0 = cfg.CAM_PITCH_START
    follow.add_look(0.0, 50.0)
    fp.add_look(0.0, 50.0)
    assert (follow.orbit_pitch - p0) * (fp.orbit_pitch - p0) < 0.0


def test_pitch_clamps_to_limits():
    # the two extreme vertical inputs hit the two pitch limits (regardless of invert-Y)
    a = _camera()
    a.add_look(0.0, 100000.0)
    b = _camera()
    b.add_look(0.0, -100000.0)
    limits = {round(cfg.CAM_PITCH_MIN, 5), round(cfg.CAM_PITCH_MAX, 5)}
    assert {round(a.orbit_pitch, 5), round(b.orbit_pitch, 5)} == limits


def test_zoom_clamps_distance():
    cam = _camera()
    cam.zoom(1000.0)   # zoom in hard
    assert math.isclose(cam.distance, cfg.CAM_DISTANCE_MIN)
    cam.zoom(-1000.0)  # zoom out hard
    assert math.isclose(cam.distance, cfg.CAM_DISTANCE_MAX)


def test_world_yaw_holds_when_boat_turns():
    cam = _camera()
    cam.add_look(50.0, 0.0)
    held = cam.orbit_yaw
    cam.app.boat.yaw = 2.0            # boat turns
    cam.app.boat.forward = glm.vec3(math.sin(2.0), 0.0, math.cos(2.0))
    cam.update(0.1)
    assert cam.orbit_yaw == held      # orbit angle is world-space, unaffected by boat heading
