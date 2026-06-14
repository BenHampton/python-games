import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import gen_islands  # noqa: E402

ISLAND = {'name': 't', 'pos': (0, 0, 0), 'scale': 20.0, 'yaw': 0.0, 'seed': 5, 'kind': 'island'}
REEF = {'name': 'r', 'pos': (0, 0, 0), 'scale': 20.0, 'yaw': 0.0, 'seed': 5, 'kind': 'reef'}


def test_generation_is_deterministic_for_a_seed():
    a = gen_islands.gen_island(ISLAND, 0)[0]
    b = gen_islands.gen_island(ISLAND, 0)[0]
    assert np.array_equal(a, b)


def test_lod0_has_more_geometry_than_lod1():
    lod0 = gen_islands.gen_island(ISLAND, 0)[0]
    lod1 = gen_islands.gen_island(ISLAND, 1)[0]
    assert len(lod0) > len(lod1)  # lod0 adds trees/spires; finer terrain


def test_reef_stays_low():
    pos = gen_islands.gen_island(REEF, 0)[0]
    assert pos[:, 1].max() < 0.2  # model-space height before world scaling


def test_different_seeds_differ():
    a = gen_islands.gen_island({**ISLAND, 'seed': 1}, 0)[0]
    b = gen_islands.gen_island({**ISLAND, 'seed': 2}, 0)[0]
    assert a.shape != b.shape or not np.array_equal(a, b)
