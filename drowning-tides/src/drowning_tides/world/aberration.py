"""Chromatic-aberration driver (phase 5): the uncanny 'reality breaks down' amount, ramped
by night + storms, with a decaying spike when an aberrated fish is caught. Fed to post.frag.
"""
from drowning_tides.config import settings as cfg


class Aberration:
    def __init__(self, app):
        self.app = app
        self.spike = 0.0

    def catch(self):
        self.spike = cfg.ABERRATION_CATCH

    def update(self, dt):
        self.spike = max(0.0, self.spike - cfg.ABERRATION_DECAY * dt)

    def amount(self):
        night = 1.0 - self.app.daycycle.day_factor
        storm = self.app.weather.storm_intensity
        val = cfg.ABERRATION_NIGHT * night + cfg.ABERRATION_STORM * storm + self.spike
        return min(val, cfg.ABERRATION_MAX)
