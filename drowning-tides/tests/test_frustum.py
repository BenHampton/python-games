from pyglm import glm

from drowning_tides.core.frustum import extract_planes, sphere_visible


def _vp():
    proj = glm.perspective(glm.radians(55.0), 16 / 9, 0.1, 2000.0)
    view = glm.lookAt(glm.vec3(0, 0, 0), glm.vec3(0, 0, -1), glm.vec3(0, 1, 0))
    return proj * view


def test_sphere_in_front_is_visible():
    planes = extract_planes(_vp())
    assert sphere_visible(planes, glm.vec3(0, 0, -50), 5.0)


def test_sphere_behind_camera_is_culled():
    planes = extract_planes(_vp())
    assert not sphere_visible(planes, glm.vec3(0, 0, 50), 5.0)


def test_sphere_far_to_the_side_is_culled():
    planes = extract_planes(_vp())
    assert not sphere_visible(planes, glm.vec3(1000, 0, -50), 5.0)


def test_big_sphere_straddling_edge_still_visible():
    planes = extract_planes(_vp())
    # off to the side but huge radius -> its sphere still intersects the frustum
    assert sphere_visible(planes, glm.vec3(60, 0, -50), 80.0)
