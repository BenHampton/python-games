import random

from drowning_tides.config import settings as cfg
from drowning_tides.world.weather import FogBank, Weather


def test_phase_cycle_order():
    w = Weather()
    w._enter('calm')
    seq = [w.phase]
    for _ in range(4):
        w._advance()
        seq.append(w.phase)
    assert seq == ['calm', 'buildup', 'hold', 'ease', 'calm']


def test_intensity_stays_in_unit_range():
    random.seed(1234)
    w = Weather()
    for _ in range(5000):
        w.update(0.016)
        assert 0.0 <= w.storm_intensity <= 1.0


def test_kill_storm_decays_target():
    w = Weather()
    w.start_storm()
    w.target = 0.8
    w.kill_storm()
    assert w.phase == 'kill'
    w.update(0.1)
    assert w.target < 0.8


def test_current_vector_zero_when_calm():
    w = Weather()
    w.storm_intensity = 0.0
    c = w.current_vector()
    assert c.x == 0.0 and c.z == 0.0


def test_fog_intensity_stays_in_unit_range():
    random.seed(99)
    w = Weather()
    for _ in range(5000):
        w.update(0.016)
        assert 0.0 <= w.fog_intensity <= 1.0


def test_fog_bank_active_time_capped():
    random.seed(7)
    # force many fog events and confirm none schedules beyond the cap
    for _ in range(200):
        fb = FogBank()
        fb.start()
        assert fb.buildup + fb.hold + fb.ease <= cfg.FOG_MAX_DURATION + 1e-6


def test_kill_fog_decays_intensity():
    w = Weather()
    w.start_fog()
    w.fog.target = 0.9
    w.fog.intensity = 0.9
    w.kill_fog()
    assert w.fog.phase == 'kill'
    w.update(0.2)
    assert w.fog.target < 0.9
