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


def disembark_pos(item_xz, center, offset):
    """Horizontal landing spot when leaving a mounted item: just inland of the item (toward the
    island centre), stepping off the boat onto the dock beside it. Returns (xz, inland)."""
    d = center - item_xz
    d = glm.normalize(d) if glm.length(d) > 1e-6 else glm.vec2(1.0, 0.0)
    return item_xz + d * offset, d


class Player:
    def __init__(self, app):
        self.app = app
        self.position = glm.vec3(0.0, 0.0, 0.0)
        self.island = None

    def disembark(self, item_pos, island):
        """Step off a mounted item (the boat) onto the walkable surface right beside it, facing
        inland so W walks up the dock into the town."""
        center = glm.vec2(island.position.x, island.position.z)
        item_xz = glm.vec2(item_pos.x, item_pos.z)
        place, inland = disembark_pos(item_xz, center, cfg.DISEMBARK_OFFSET)
        self.island = island
        ground = island.ground_y(place.x, place.y)
        town = getattr(self.app, 'town', None)
        deck = town.deck_height(place.x, place.y) if town is not None else None
        y = max(ground, deck) if deck is not None else ground
        self.position = glm.vec3(place.x, y, place.y)
        self.app.camera.orbit_yaw = math.atan2(inland.x, inland.y)   # face inland / the town

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
