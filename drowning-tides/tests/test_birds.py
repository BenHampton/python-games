import math

from pyglm import glm

from drowning_tides.config import settings as cfg
from drowning_tides.world.birds import climb_step, flee_velocity, should_flee


def test_should_flee_inside_and_outside_range():
    assert should_flee(cfg.BIRD_FLEE_RANGE - 0.5, cfg.BIRD_FLEE_RANGE)
    assert not should_flee(cfg.BIRD_FLEE_RANGE + 0.5, cfg.BIRD_FLEE_RANGE)


def test_flee_velocity_points_away_at_speed():
    bird = glm.vec2(10.0, 0.0)
    threat = glm.vec2(4.0, 0.0)              # threat to the -x side -> flee toward +x
    v = flee_velocity(bird, threat, cfg.BIRD_FLEE_SPEED)
    assert v.x > 0 and abs(v.y) < 1e-6
    assert math.isclose(glm.length(v), cfg.BIRD_FLEE_SPEED, rel_tol=1e-6)


def test_flee_velocity_handles_threat_on_top():
    v = flee_velocity(glm.vec2(5.0, 5.0), glm.vec2(5.0, 5.0), cfg.BIRD_FLEE_SPEED)
    assert math.isclose(glm.length(v), cfg.BIRD_FLEE_SPEED, rel_tol=1e-6)   # picks a fallback dir


def test_climb_step_eases_toward_target_without_overshoot():
    y = 0.6
    for _ in range(2000):
        y = climb_step(y, cfg.BIRD_CRUISE_Y, cfg.BIRD_CLIMB_RATE, 0.05)
        assert y <= cfg.BIRD_CRUISE_Y + 1e-6
    assert math.isclose(y, cfg.BIRD_CRUISE_Y, abs_tol=1e-2)                 # converges to cruise
