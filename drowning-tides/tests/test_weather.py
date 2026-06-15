import random

from drowning_tides.config import settings as cfg
from drowning_tides.world.weather import FogBank, RainState, Weather


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


def test_cloud_cover_stays_in_unit_range():
    random.seed(3)
    w = Weather()
    for _ in range(3000):
        w.update(0.016)
        assert 0.0 <= w.cloud_cover <= 1.0


def test_lightning_stays_in_range_and_calm_is_dark():
    w = Weather()
    w.storm_intensity = 0.0
    for _ in range(500):
        w._update_lightning(0.016)
    assert w.lightning < 1e-3           # no spontaneous flashes out of a storm

    random.seed(8)
    w.start_storm()
    for _ in range(3000):
        w.update(0.016)
        assert 0.0 <= w.lightning <= 1.0


def test_strike_flashes_and_spawns_bolt():
    w = Weather()
    w.strike()
    assert w.bolt_active
    w._update_lightning(0.0)            # first flicker spike fires immediately
    assert w.lightning > 0.5


def test_rain_intensity_stays_in_unit_range():
    random.seed(321)
    w = Weather()
    for _ in range(8000):
        w.update(0.016)
        assert 0.0 <= w.rain_intensity <= 1.0


def test_rain_can_fall_without_a_storm():
    # the rain scheduler runs independently: a forced event raises rain while storm stays calm
    r = RainState()
    r.start()
    for _ in range(int(r.buildup / 0.05) + 5):
        r.update(0.05, 0.0)             # storm_rain = 0 (no storm)
    assert r.intensity > 0.05           # it's raining with no storm at all


def test_rainy_storm_drives_rain_but_dry_storm_does_not():
    # storm_rain floor lifts rain immediately even from a clear schedule...
    r = RainState()
    for _ in range(20):
        r.update(0.05, 0.7)
    assert r.intensity > 0.2
    # ...and a dry storm (storm_rain = 0) leaves the clear schedule untouched early on
    r2 = RainState()
    before = r2.intensity
    r2.update(0.05, 0.0)
    assert r2.intensity <= before + 1e-6


def test_rain_peaks_span_drizzle_to_shower():
    random.seed(5)
    peaks = []
    for _ in range(300):
        r = RainState()
        r.start()
        peaks.append(r.peak)
    assert min(peaks) < 0.3 and max(peaks) > 0.6      # both drizzle and heavier showers occur


def test_kill_rain_decays_intensity():
    w = Weather()
    w.start_rain()
    w.rain.target = 0.9
    w.rain.intensity = 0.9
    w.kill_rain()
    assert w.rain.phase == 'kill'
    w.update(0.2)
    assert w.rain.target < 0.9


def test_some_storms_are_dry():
    # over many storms, STORM_RAIN_CHANCE < 1 means at least one dry (gain 0) storm occurs
    random.seed(11)
    gains = []
    w = Weather()
    for _ in range(200):
        w._enter('buildup')
        gains.append(w._storm_rain_gain)
    assert any(g == 0.0 for g in gains) and any(g > 0.0 for g in gains)
