import pygame as pg
from ground_weapon import GroundShotgun, GroundAxe, GroundChaingun, GroundPlasmaRifle, GroundBFG
from settings import TEST_SPAWN_COVERAGE_DIM
from map_level.test_map import *
from map_level.level_one import *
from map_level.level_two import *
from map_level.level_three import *
from map_level.level_four import *

MAPS =  [level_one, level_two, level_three, level_four]
# MAPS =  [test, level_one, level_two, level_three, level_four] # for test Map

class Map:
    def __init__(self, game):
        self.game = game
        self.current_map = MAPS[self.game.current_level]
        self.world_map = {}
        self.world_spawn_map = {}
        self.door_interation_coords = {}
        self.door_coords = {}

        self.rows = len(self.current_map)
        self.cols = len(self.current_map[0])
        self.get_map()

        self.boss_spawn_coords = {}
        self.spawn_coords = self.handle_available_npc_spawn_coords()

        self.map_weapons = []
        self.handle_map_weapons()

        self.ways = [-1, 0], [0, -1], [1, 0], [0, 1], [-1, -1], [1, 1]
        self.graph = {}

    def handle_available_npc_spawn_coords(self):
        match self.game.current_level:
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
                spawn_coords.update({(x, y) for x in range(1, self.cols - 1) for y in range(9, 13)})
                spawn_coords.update({(x, y) for x in range(3, self.cols - 1) for y in range(14, 21)})

                # self.boss_spawn_coords = {(x, y) for x in range(4, self.cols - 5) for y in range(28, self.rows - 3)}
                self.handle_available_boss_npc_spawn_coords(4, 5, 28, 3)
                return spawn_coords

            case 3:
                spawn_coords = {(x, y) for x in range(13, self.cols - 5) for y in range(2, 7)}
                spawn_coords.update({(x, y) for x in range(6, 8) for y in range(5, 7)})
                spawn_coords.update({(x, y) for x in range(3, self.cols - 1) for y in range(12, 20)})
                spawn_coords.update({(x, y) for x in range(8, self.cols - 3) for y in range(22, 32)})

                # self.boss_spawn_coords = {(x, y) for x in range(1, self.cols - 1) for y in range(42, self.rows - 1)}
                # self.handle_available_boss_npc_spawn_coords(1, 1, 42, 1)
                return spawn_coords
            case _:
                return {(x, y) for x in range(0, self.cols) for y in range(0, self.rows)}

    def handle_available_boss_npc_spawn_coords(self, x_one, y_one, x_two, y_two):
            self.boss_spawn_coords = {(x, y) for x in range(x_one, self.cols - y_one) for y in range(x_two, self.rows - y_two)}

    def handle_map_weapons(self):
        match self.game.current_level:
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

    def handle_open_door(self, pos):
        x, y = pos
        print('handle_open_door: ', pos)
        self.door_interation_coords.pop((x, y))
        x_offset = x
        y_offset = y + 1

        print('offset: ', (x_offset, y_offset))
        self.door_coords.pop((x_offset, y_offset))
        self.world_map.pop((x_offset, y_offset))

    def get_map(self):
        for j, row in enumerate(self.current_map):
            for i, value in enumerate(row):
                if value:
                    self.world_map[(i,j)] = value
                    self.world_spawn_map[(i, j)] = value
                    if value == 8: # (x/a, y/b)
                        a = i
                        b = j - 1
                        self.door_interation_coords[(a, b)] = (a, b)
                        self.door_coords[(i, j)] = value
                        print('door_coords: ', self.door_coords)
                        print('door_interation_coords: ', self.door_interation_coords)

        for j, row in enumerate(self.current_map):
            for i, value in enumerate(row):
                if not value:
                    self.world_spawn_map[(i, j)] = True

    # def get_door_coords(self):

    #todo use test map to write method that sets the  x/yoffset to the applicable door__coord
    # def get_next_nodes(self, x, y):
    #     return [(x + dx, y + dy) for dx, dy in self.ways if (x + dx, y + dy) not in self.game.map.world_map]
    #
    # def get_graph(self):
    #     for y, row in enumerate(self.current_map):
    #         for x, col in enumerate(row):
    #             if not col:
    #                 self.graph[(x, y)] = self.graph.get((x, y), []) + self.get_next_nodes(x, y)

    def draw_for_test(self):

        dim = TEST_SPAWN_COVERAGE_DIM[self.game.current_level]

        for pos in self.world_spawn_map:
            color = 'darkgray'
            block_width = 2
            if pos in self.door_interation_coords:
                color = 'purple'  # spawn door
                # todo params -> Rect( (left, top), (width, height))
                pg.draw.rect(self.game.screen, color, (pos[0] * dim , pos[1] * dim, dim, dim), 100)
                # pg.draw.rect(self.game.screen, color, (pos[0] * dim, pos[1] * dim, dim, dim), 5)
                continue
            elif pos not in self.world_map and pos in self.spawn_coords:
                if pos in self.boss_spawn_coords:
                    color = 'green'  # spawn final boss
                else:
                    color = 'blue' #(243, 18, 153) #'dark red' # in spawn but is a wall
            elif pos in self.spawn_coords:
                color = 'red' # spawn-able
                block_width = 3
            elif pos in self.boss_spawn_coords:
                color = 'green'  # spawn final boss
            elif pos not in self.world_map:
                color = 'black' # not spawn-able

            # todo params -> Rect( (left, top), (width, height))
            pg.draw.rect(self.game.screen, color, (pos[0] * dim, pos[1] * dim, dim, dim), block_width)






















