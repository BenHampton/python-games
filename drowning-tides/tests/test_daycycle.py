from pyglm import glm

from drowning_tides.world.daycycle import DayCycle


def test_time_wraps_unit_interval():
    dc = DayCycle(t=0.95, timescale=1.0)
    # advance well past 1.0 worth of phase and confirm it wraps
    for _ in range(100):
        dc.update(10.0)
        assert 0.0 <= dc.t < 1.0


def test_sun_dir_is_unit_and_moon_opposite():
    for t in (0.0, 0.25, 0.5, 0.75, 0.9):
        dc = DayCycle(t=t)
        assert abs(glm.length(dc.sun_dir) - 1.0) < 1e-5
        assert glm.length(dc.sun_dir + dc.moon_dir) < 1e-5  # moon == -sun


def test_day_factor_and_stars_inverse_and_bounded():
    for t in (0.0, 0.25, 0.5, 0.75):
        dc = DayCycle(t=t)
        assert 0.0 <= dc.day_factor <= 1.0
        assert 0.0 <= dc.star_alpha <= 1.0
        assert abs((dc.day_factor + dc.star_alpha) - 1.0) < 1e-6


def test_noon_brighter_than_midnight():
    noon = DayCycle(t=0.5)
    midnight = DayCycle(t=0.0)
    assert noon.day_factor > midnight.day_factor
    assert noon.palette.sun_strength > midnight.palette.sun_strength
    assert noon.sun_dir.y > 0.0      # sun up at noon
    assert midnight.sun_dir.y < 0.0  # sun down at midnight


def test_set_time_setter():
    dc = DayCycle(t=0.1)
    dc.set_time(1.75)  # wraps to 0.75
    assert abs(dc.t - 0.75) < 1e-9
