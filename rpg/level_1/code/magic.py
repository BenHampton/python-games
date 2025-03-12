import pygame as pg
from random import randint

from rpg.level_1.code.settings import TILESIZE
from support import *

class MagicPlayer:
    def __init__(self, animation_player):
        self.animation_player = animation_player

    def heal(self, player, strength, cost, groups):
        # if player.health != player.stats['health']:
        if player.energy >= cost:
            player.health += strength
            player.energy -= cost
            if player.health >= player.stats['health']:
                player.health = player.stats['health']
            offset = pg.math.Vector2(0, -60) #optinoal
            self.animation_player.create_particles('aura', player.rect.center, groups)
            self.animation_player.create_particles('heal', player.rect.center + offset, groups)

    def flame(self, player, cost, groups):
        if player.energy >= cost:
            player.energy -= cost

            player_direction =  player.status.split('_')[0]

            if player_direction == 'right': direction = pg.math.Vector2(1, 0)
            elif player_direction == 'left': direction = pg.math.Vector2(-1, 0)
            elif player_direction == 'up': direction = pg.math.Vector2(0, -1)
            else: direction = pg.math.Vector2(0, 1)

            for i in range(1, 6):
                if direction.x: #horizontal
                    offset_x = (direction.x *  i) * int(TILESIZE)
                    x = player.rect.centerx + offset_x + randint(-TILESIZE // 3, TILESIZE // 3)
                    y = player.rect.centery + randint(-TILESIZE // 3, TILESIZE // 3)
                else: #vertical
                    offset_y = (direction.y *  i) * int(TILESIZE)
                    x = player.rect.centerx + randint(-TILESIZE // 3, TILESIZE // 3)
                    y = player.rect.centery + offset_y + randint(-TILESIZE // 3, TILESIZE // 3)
                self.animation_player.create_particles('flame', (x, y), groups)
