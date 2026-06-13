import math

from pyglm import glm

from drowning_tides.config import settings as cfg
from drowning_tides.world.waves import WaveField


def test_sample_is_finite_and_deterministic():
    wf = WaveField()
    wf.recompute(glm.vec2(1.0, 0.0), 0.5)

    h1, n1 = wf.sample(12.0, -7.0, 3.0)
    h2, n2 = wf.sample(12.0, -7.0, 3.0)

    assert math.isfinite(h1)
    assert h1 == h2
    assert (n1.x, n1.y, n1.z) == (n2.x, n2.y, n2.z)
    # normal is unit length and points generally upward
    assert abs(glm.length(n1) - 1.0) < 1e-5
    assert n1.y > 0.0


def test_total_amplitude_clamped_at_full_storm():
    wf = WaveField()
    wf.recompute(glm.vec2(1.0, 0.0), 1.0)
    assert sum(wf.amp) <= cfg.WAVE_MAX_AMPLITUDE + 1e-5


def test_calm_amplitude_below_storm():
    wf = WaveField()
    wf.recompute(glm.vec2(1.0, 0.0), 0.0)
    calm_total = sum(wf.amp)
    wf.recompute(glm.vec2(1.0, 0.0), 1.0)
    storm_total = sum(wf.amp)
    assert calm_total < storm_total
