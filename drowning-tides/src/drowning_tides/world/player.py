"""On-foot (first-person) player. Active only while disembarked (`game_state.ON_FOOT`):
walks WASD on a flat stand-in land plane, bound to the island disc it landed on. The camera
owns the look angles (mouse-look); movement uses the same yaw convention so it matches the
view. No terrain collision yet — the land plane is a placeholder.
"""
import math

import pygame as pg
from pyglm import glm

from drowning_tides.config import settings as cfg


def walk(pos, yaw, fwd, strafe, dt, center, radius, land_y, speed):
    """Pure step: move (pos) by WASD along the look yaw, clamped to the island disc."""
    s, c = math.sin(yaw), math.cos(yaw)
    move = glm.vec2(s, c) * fwd + glm.vec2(-c, s) * strafe   # forward, right (= cross(fwd, up))
    x, z = pos.x, pos.z
    if glm.length(move) > 1e-6:
        step = glm.normalize(move) * speed * dt
        x += step.x
        z += step.y
    dx, dz = x - center.x, z - center.y
    d = math.hypot(dx, dz)
    if d > radius:
        x = center.x + dx / d * radius
        z = center.y + dz / d * radius
    return glm.vec3(x, land_y, z)


class Player:
    def __init__(self, app):
        self.app = app
        self.position = glm.vec3(0.0, 0.0, 0.0)
        self.island = None

    def spawn(self, island, boat_pos):
        """Land on the island's shore nearest the boat and face inland."""
        center = glm.vec2(island.position.x, island.position.z)
        d = glm.vec2(boat_pos.x, boat_pos.z) - center
        d = glm.normalize(d) if glm.length(d) > 1e-6 else glm.vec2(1.0, 0.0)
        landing = center + d * (island.radius * island.spawn_frac)
        self.island = island
        self.position = glm.vec3(landing.x, island.ground_y(landing.x, landing.y), landing.y)
        self.app.camera.orbit_yaw = math.atan2(d.x, d.y)     # face the boat / open sea

    def update(self, dt):
        if self.island is None or not self.app.game_state.is_on_foot() or self.app.console.active:
            return
        keys = pg.key.get_pressed()
        fwd = float(keys[cfg.KEYS['THROTTLE_UP']]) - float(keys[cfg.KEYS['THROTTLE_DOWN']])
        strafe = float(keys[cfg.KEYS['TURN_RIGHT']]) - float(keys[cfg.KEYS['TURN_LEFT']])
        center = glm.vec2(self.island.position.x, self.island.position.z)
        walk_radius = self.island.radius * self.island.walk_frac
        prev = glm.vec3(self.position)
        # move freely (no disc clamp here), then resolve boundaries below
        p = walk(self.position, self.app.camera.orbit_yaw, fwd, strafe, dt,
                 center, 1e9, self.island.land_y, cfg.PLAYER_SPEED)
        town = getattr(self.app, 'town', None)
        x, z = town.collide(p.x, p.z, cfg.PLAYER_RADIUS) if town is not None else (p.x, p.z)
        deck = town.deck_height(x, z) if town is not None else None
        d = math.hypot(x - center.x, z - center.y)
        if deck is not None:                                  # standing on a plank dock
            self.position = glm.vec3(x, max(self.island.ground_y(x, z), deck), z)
        elif d <= walk_radius:                                # on the island
            self.position = glm.vec3(x, self.island.ground_y(x, z), z)
        else:
            # off the shelf and not on a dock: slide along the shore if we came from land,
            # otherwise (stepping off a dock edge) stay put — don't walk onto open water
            prev_deck = town.deck_height(prev.x, prev.z) if town is not None else None
            prev_d = math.hypot(prev.x - center.x, prev.z - center.y)
            if prev_deck is None and prev_d <= walk_radius and d > 1e-6:
                x = center.x + (x - center.x) / d * walk_radius
                z = center.y + (z - center.y) / d * walk_radius
                self.position = glm.vec3(x, self.island.ground_y(x, z), z)
            else:
                self.position = prev
