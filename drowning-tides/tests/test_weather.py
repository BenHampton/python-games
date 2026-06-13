import random

from drowning_tides.world.weather import Weather


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
