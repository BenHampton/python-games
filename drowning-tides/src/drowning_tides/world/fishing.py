"""Fishing (no economy yet): cast from the helm over open water, wait for a bite, pull up a
random fish from cfg.FISH_TABLE. Aberrated catches spike the chromatic aberration (phase 5).
"""
import random

from drowning_tides.config import settings as cfg


class Fishing:
    def __init__(self, app):
        self.app = app
        self.casting = False
        self.timer = 0.0
        self.rng = random.Random()

    def cast(self):
        if not self.app.game_state.is_helm() or self.casting:
            return
        if self.app.islands.nearest_dockable(self.app.boat.position) is not None:
            self.app.hud.show("Too close to shore to fish.", 2.0)
            return
        self.casting = True
        self.timer = cfg.FISH_CAST_TIME
        self.app.hud.show("Casting…", cfg.FISH_CAST_TIME + 0.2)

    def update(self, dt):
        if not self.casting:
            return
        self.timer -= dt
        if self.timer <= 0.0:
            self.casting = False
            name, aberrated = self.roll()
            if aberrated:
                self.app.aberration.catch()
                self.app.hud.show(f"Something wrong surfaces… a {name}.", 4.5)
            else:
                self.app.hud.show(f"Caught a {name}!", 3.0)

    def roll(self):
        weights = [f[1] for f in cfg.FISH_TABLE]
        i = self.rng.choices(range(len(cfg.FISH_TABLE)), weights=weights)[0]
        name, _, aberrated = cfg.FISH_TABLE[i]
        return name, aberrated
