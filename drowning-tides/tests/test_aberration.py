from types import SimpleNamespace

from drowning_tides.config import settings as cfg
from drowning_tides.world.aberration import Aberration


def _app(day_factor, storm):
    return SimpleNamespace(
        daycycle=SimpleNamespace(day_factor=day_factor),
        weather=SimpleNamespace(storm_intensity=storm),
    )


def test_calm_daylight_has_no_aberration():
    assert Aberration(_app(1.0, 0.0)).amount() == 0.0


def test_night_and_storm_ramp_and_clamp():
    a = Aberration(_app(0.0, 1.0))   # full night + full storm
    assert a.amount() > 0.0
    assert a.amount() <= cfg.ABERRATION_MAX


def test_catch_spike_decays():
    a = Aberration(_app(1.0, 0.0))
    a.catch()
    peak = a.amount()
    assert peak > 0.0
    a.update(1.0)
    assert a.amount() < peak
