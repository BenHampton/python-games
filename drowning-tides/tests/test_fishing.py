import random

from drowning_tides.config import settings as cfg
from drowning_tides.world.fishing import Fishing


def _fishing(seed=0):
    f = Fishing.__new__(Fishing)   # skip app wiring
    f.rng = random.Random(seed)
    return f


def test_roll_returns_valid_table_entry_with_matching_flag():
    f = _fishing()
    by_name = {x[0]: x[2] for x in cfg.FISH_TABLE}
    for _ in range(80):
        name, aberrated = f.roll()
        assert name in by_name
        assert aberrated == by_name[name]


def test_roll_yields_both_common_and_aberrated():
    f = _fishing(1)
    flags = [f.roll()[1] for _ in range(800)]
    assert any(flags) and not all(flags)
