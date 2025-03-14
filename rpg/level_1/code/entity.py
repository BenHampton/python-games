import pygame as pg
from math import sin

class Entity(pg.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.frame_index = 0
        self.animation_speed = 0.15
        # ___   ___
        # | x:  0 |
        # | y:  0 |
        # |__   __|
        self.direction = pg.math.Vector2()

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')
        self.rect.center = self.hitbox.center

    def collision(self, direction):
            if direction == 'horizontal':
                for sprite in self.obstacle_sprites:
                    if sprite.hitbox.colliderect(self.hitbox):
                        if self.direction.x > 0:  # player is moving right
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0:  # player is moving left
                            self.hitbox.left = sprite.hitbox.right
            elif direction == 'vertical':
                for sprite in self.obstacle_sprites:
                    if sprite.hitbox.colliderect(self.hitbox):
                        if self.direction.y > 0:  # player is moving down
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0:  # player is moving up
                            self.hitbox.top = sprite.hitbox.bottom

    def wave_value(self):
        value = sin(pg.time.get_ticks())
        if value >0:
            return 255
        return  0