import os
import random
import math
import pygame as pg
from os import listdir
from os.path import isfile, join

pg.init()

pg.display.set_caption("Platformer")

BG_COLOR = (255, 255, 255)
WIDTH, HEIGHT = 1000, 800
FPS = int(60)
PLAYER_VEL = 5

window = pg.display.set_mode((WIDTH, HEIGHT))

def main(window):
    clock = pg.time.Clock()

    run = True
    while run:
        clock.tick(FPS)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
                break


if __name__ == "__main__":
    main(window)