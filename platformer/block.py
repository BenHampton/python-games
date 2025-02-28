from object import *
from os.path import join

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        self.size = size
        block = self.get_block(self.size)
        self.image.blit(block, (0, 0))
        self.mask = pg.mask.from_surface(self.image)

    def get_block(self, size):
        path = join('assets', 'Terrain', "Terrain.png")
        image = pg.image.load(path).convert_alpha()
        surface = pg.Surface((size, size), pg.SRCALPHA, 32)
        rect = pg.Rect(96, 0, size, size)
        surface.blit(image, (0, 0), rect)
        return pg.transform.scale2x(surface)