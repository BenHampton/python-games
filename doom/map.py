import pygame as pg
from map_level.level_one import *
from map_level.level_two import *
from map_level.level_three import *
from map_level.level_four import *

class Map:
    def __init__(self, game):
        self.game = game
        self.all_maps = [level_one, level_two, level_three, level_four]
        self.current_map = self.all_maps[self.game.map_level]
        self.world_map = {}
        self.rows = len(self.current_map)
        self.cols = len(self.current_map[0])
        self.get_map()

    def get_map(self):
        for j, row in enumerate(self.current_map):
            for i, value in enumerate(row):
                if value:
                    self.world_map[(i,j)] = value

    def draw(self):
        [pg.draw.rect(self.game.screen, 'darkgray', (pos[0] * 100, pos[1] * 100, 100, 100), 2)
         for pos in self.world_map]


















