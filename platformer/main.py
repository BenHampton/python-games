import os
import random
import math
import pygame as pg
from os import listdir
from os.path import isfile, join

pg.init()

pg.display.set_caption("Platformer")

WIDTH, HEIGHT = 1000, 800
FPS = int(60)
PLAYER_VEL = 5

window = pg.display.set_mode((WIDTH, HEIGHT))

class Player(pg.sprite.Sprite):
    COLOR = (255, 0, 0)

    def __init__(self, x, y, width, height):
        self.rect = pg.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        if self.direction != 'right':
            self.direction = "right"
            self.animation_count = 0

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != 'left':
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.y_vel = vel

def get_background(name):
    image = pg.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []
    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)
    return tiles, image

def draw(window, background, bg_image):
    for tile in background:
        window.blit(bg_image, tile)

    pg.display.update()

def main(window):
    clock = pg.time.Clock()
    background, bg_image = get_background("Blue.png")

    run = True
    while run:
        clock.tick(FPS)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
                break

        draw(window, background, bg_image)

if __name__ == "__main__":
    main(window)