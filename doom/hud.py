import pygame as pg
from settings import *

class Hud:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.hud_height = FULL_HEIGHT - HUD_HEIGHT
        self.hud_image = self.game.object_renderer.get_texture('resources/hud.jpg', (WIDTH, HUD_HEIGHT))
        self.digit_size = 40
        self.digit_images = [self.game.object_renderer.get_texture(f'resources/textures/digits/{i}.png', [self.digit_size] * 2)
                             for i in range(11)]
        self.digits = dict(zip(map(str, range(11)), self.digit_images))
        self.hud_width = WIDTH // 8
        self.hud_sections_start = [0, # black
                                   100, # green
                                   250, # white draw_player_health
                                   430, # yellow draw_number_pad
                                   550, # blue face 5920
                                   750, # purple draw_armor
                                   950, # orange
                                   1200] # black
        # 1300 / 2 = 650
        self.hud_sections_width = [100, # black
                                   150, # green
                                   200, # white draw_player_health
                                   150, # yellow draw_number_pad
                                   200, # blue face
                                   200, #purple draw_armor
                                   250, # orange
                                   100] # black

    def draw(self):
        # self.draw_background()
        self.draw_ammo()
        self.draw_player_health()
        self.draw_number_pad()
        self.draw_face()
        self.draw_armor()
        self.draw_inventory()
        self.draw_padding_blocks()


    def draw_padding_blocks(self):
        # # todo Rect((left, top), (width, height)) -> Rect
        pg.draw.rect(self.game.screen, 'black',
                     (self.hud_sections_start[0],
                      FULL_HUB_HEIGHT,
                      self.hud_sections_width[0],
                      FULL_HUB_HEIGHT))
        pg.draw.rect(self.game.screen, 'black',
                     (self.hud_sections_start[7],
                      FULL_HUB_HEIGHT,
                      self.hud_sections_width[7],
                      FULL_HUB_HEIGHT))

    def draw_ammo(self):
        pg.draw.rect(self.game.screen, 'green',
                     (self.hud_sections_start[1],
                      FULL_HUB_HEIGHT ,
                      self.hud_sections_width[1],
                      FULL_HUB_HEIGHT))

    def draw_player_health(self):
        pg.draw.rect(self.game.screen, 'white',
                     (self.hud_sections_start[2],
                      FULL_HUB_HEIGHT,
                      self.hud_sections_width[2],
                      FULL_HUB_HEIGHT))
        # health = str(self.game.player.health)
        # for i, char in enumerate(health):
        #     self.screen.blit(self.digits[char], (i * self.digit_size + 250, FULL_HUB_HEIGHT + 30))
        # self.screen.blit(self.digits['10'], ((i + 1) * self.digit_size + 250, FULL_HUB_HEIGHT + 30))

    def draw_number_pad(self):
        pg.draw.rect(self.game.screen, 'yellow',
                     (self.hud_sections_start[3],
                      FULL_HUB_HEIGHT,
                      self.hud_sections_width[3],
                      FULL_HUB_HEIGHT))

    def draw_face(self):
        pg.draw.rect(self.game.screen, 'blue',
                     (self.hud_sections_start[4],
                      FULL_HUB_HEIGHT,
                      self.hud_sections_width[4],
                      FULL_HUB_HEIGHT))

    def draw_armor(self):
        pg.draw.rect(self.game.screen, 'purple',
                     (self.hud_sections_start[5],
                      FULL_HUB_HEIGHT,
                      self.hud_sections_width[5],
                      FULL_HUB_HEIGHT))

    def draw_inventory(self):
        pg.draw.rect(self.game.screen, 'orange',
                     (self.hud_sections_start[6],
                      FULL_HUB_HEIGHT,
                      self.hud_sections_width[6],
                      FULL_HUB_HEIGHT))

    def draw_background(self):
        self.screen.blit(self.hud_image, (0, self.hud_height))




