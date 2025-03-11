import pygame as pg
import sys
from settings import *
from level import *

class Game:
    def __init__(self):

        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGTH))
        self.clock = pg.time.Clock()

        self.level = Level()

    def run(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                    pg.quit()
                    sys.exit()

            self.screen.fill('black')
            pg.display.set_caption('TODO')

            self.level.run()

            pg.display.update()
            self.clock.tick(FPS)

if __name__ == '__main__':
    game = Game()
    game.run()
