import pygame as pg
from os import listdir
from os.path import isfile, join

class Utility:

    @staticmethod
    def load_sprite_sheets(dir1, dir2, width, height, direction=False):
        path = join('assets', dir1, dir2)
        images = [f for f in listdir(path) if isfile(join(path, f))]

        all_sprites = {}

        for image in images:
            sprite_sheet = pg.image.load(join(path, image)).convert_alpha()

            sprites = []
            for i in range(sprite_sheet.get_width() // width):
                surface = pg.Surface((width, height), pg.SRCALPHA, 32)
                rect = pg.Rect(i * width, 0, width, height)
                surface.blit(sprite_sheet, (0, 0), rect)
                sprites.append(pg.transform.scale2x(surface))

            if direction:
                all_sprites[image.replace(".png", "") + "_right"] = sprites
                all_sprites[image.replace(".png", "") + "_left"] = Utility.flip(sprites)
            else:
                all_sprites[image.replace(".png", "")] = sprites

        return  all_sprites

    @staticmethod
    def flip(sprites):
        return [pg.transform.flip(sprite, True, False) for sprite in sprites]