import pygame as pg
from map_level.level_one import *
from map_level.level_two import *
from map_level.level_three import *
from map_level.level_four import *
from doom.ground_weapon import GroundShotgun, GroundAxe, GroundChaingun, GroundPlasmaRifle, GroundBFG

class Map:
    def __init__(self, game):
        self.game = game
        self.all_maps = [level_one, level_two, level_three, level_four]
        self.current_map = self.all_maps[self.game.map_level]
        self.world_map = {}
        self.world_spawn_map = {}
        self.rows = len(self.current_map)
        self.cols = len(self.current_map[0])
        self.get_map()

        self.boss_spawn_coords = {}
        self.spawn_coords = self.handle_npc_spawn_coords()

        self.map_weapons = []

        self.handle_map_weapons()

    def handle_npc_spawn_coords(self):
        match self.game.map_level:
            case 0:

                # return {(x, y) for x in range(3, 6) for y in range(3, 5)} # test spawn
                spawn_coords = {(x, y) for x in range(10, self.cols - 1) for y in range(1, 8)}
                spawn_coords.update({(x, y) for x in range(1, self.cols - 1) for y in range(14, self.rows - 1)})
                return spawn_coords

            case 1:
                spawn_coords = {(x, y) for x in range(9, self.cols - 1) for y in range(1,10)}
                spawn_coords.update({(x, y) for x in range(7, self.cols - 1) for y in range(5, 10)})
                spawn_coords.update({(x, y) for x in range(1, self.cols - 1) for y in range(10, self.rows - 1)})
                return spawn_coords

            case 2:
                spawn_coords = {(x, y) for x in range(7, self.cols - 1) for y in range(1, 9)}
                spawn_coords.update({(x, y) for x in range(4, 7) for y in range(1, 3)})
                spawn_coords.update({(x, y) for x in range(1, self.cols - 1) for y in range(9, self.rows - 1)})
                spawn_coords.update({(x, y) for x in range(1, self.cols - 1) for y in range(14, self.rows - 1)})

                # self.boss_spawn_coords = {(x, y) for x in range(4, self.cols - 5) for y in range(28, self.rows - 3)}
                self.handle_boos_npc_spawn_coords(4, 5, 28, 3)
                return spawn_coords

            case 3:
                spawn_coords = {(x, y) for x in range(13, self.cols - 5) for y in range(2, 7)}
                spawn_coords.update({(x, y) for x in range(6, 8) for y in range(5, 7)})
                spawn_coords.update({(x, y) for x in range(3, self.cols - 1) for y in range(12, 20)})
                spawn_coords.update({(x, y) for x in range(8, self.cols - 3) for y in range(22, 32)})

                # self.boss_spawn_coords = {(x, y) for x in range(1, self.cols - 1) for y in range(42, self.rows - 1)}
                self.handle_boos_npc_spawn_coords(1,1,42,1)
                return spawn_coords
            case _:
                return {(x, y) for x in range(0, self.cols) for y in range(0, self.rows)}

    def handle_boos_npc_spawn_coords(self, x_one, y_one, x_two, y_two):
            self.boss_spawn_coords = {(x, y) for x in range(x_one, self.cols - y_one) for y in range(x_two, self.rows - y_two)}

    def handle_map_weapons(self):
        match self.game.map_level:
            case 0:
                self.map_weapons.append(GroundShotgun)
            case 1:
                self.map_weapons.append(GroundAxe)
            case 2:
                self.map_weapons.extend([GroundShotgun,
                                         GroundChaingun,
                                         GroundPlasmaRifle,
                                         GroundBFG])
            case 3:
                self.map_weapons.extend([GroundShotgun,
                                         GroundChaingun,
                                         GroundPlasmaRifle,
                                         GroundBFG])
            case _:
                raise Exception("No map_id found could not append map's weapons")

    def get_map(self):
        for j, row in enumerate(self.current_map):
            for i, value in enumerate(row):
                if value:
                    self.world_map[(i,j)] = value
                    self.world_spawn_map[(i, j)] = value

        for j, row in enumerate(self.current_map):
            for i, value in enumerate(row):
                if not value:
                    self.world_spawn_map[(i, j)] = True

    def draw(self):
        [pg.draw.rect(self.game.screen, 'darkgray', (pos[0] * 100, pos[1] * 100, 100, 100), 2)
         for pos in self.world_map]

    def draw_spawn_coverage(self):

        dim = self.rows if self.rows < 25 else self.rows // 2

        for pos in self.world_spawn_map:
            color  = 'darkgray'
            if pos not in self.world_map and pos in self.spawn_coords:
                if pos in self.boss_spawn_coords:
                    color = 'green'  # spawn final boss
                else:
                    color = (243, 18, 153) #'dark red' # in spawn but is a wall
            elif pos in self.spawn_coords:
                color = 'red' # spawn-able
            elif pos in self.boss_spawn_coords:
                color = 'green'  # spawn final boss
            elif pos not in self.world_map:
                color = 'black' # not spawn-able

            pg.draw.rect(self.game.screen, color, (pos[0] * dim, pos[1] * dim, dim, dim), 2)




















