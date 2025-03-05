import pygame as pg
from settings import *
from utils.utility import Utility

class Hud:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        # self.hud_height = FULL_HEIGHT - HUD_HEIGHT #HEIGHT
        self.hud_image = self.game.object_renderer.get_texture('resources/textures/hud/section_background.jpg', (WIDTH, HUD_HEIGHT))
        self.arms_image = self.game.object_renderer.get_texture('resources/textures/hud/arms_background.jpg', (WIDTH, HUD_HEIGHT))

        self.text_font = Utility.get_font('doom.ttf', 35)
        self.arms_font = Utility.get_font('doom.ttf', 18)

        self.digit_size = 40
        self.digit_images = [self.game.object_renderer.get_texture(f'resources/textures/digits/{i}.png', [self.digit_size] * 2)
                             for i in range(11)]
        self.digits = dict(zip(map(str, range(11)), self.digit_images))

        self.face_size = 90
        self.face_images = [
            self.game.object_renderer.get_texture(f'resources/textures/hud/face/{i}.png', [self.face_size] * 2)
            for i in range(2)]
        self.face_image = dict(zip(map(int, range(2)), self.face_images))

        self.hud_padding_top = 20
        self.hud_width = WIDTH // 8
        self.hud_sections_start = [0, # padding left
                                   100, # ammo
                                   250, # health
                                   425, # arms
                                   550, # face
                                   750, # armor
                                   925, # cards
                                   1000, # inventory
                                   1200] # padding right
        # 1300 / 2 = 650
        self.hud_sections_width = [100, # padding left
                                   150, # ammo
                                   175, # health
                                   125, # arms = 550
                                   200, # face
                                   175, # armor
                                   75, # cards
                                   200, # inventory
                                   100] # padding right = 725 == 1275

    def draw(self):
        self.draw_background()
        self.draw_ammo() #todo center text
        self.draw_player_health() #todo center text
        self.draw_arms()
        self.draw_face()
        self.draw_armor()
        self.draw_cards() #todo rename??
        # self.draw_inventory()


    def draw_background(self):
        # todo params -> (image, (width, height), Rect( (left, top), (width, height)) )
        for i in range (0, len(self.hud_sections_width)):
            self.screen.blit(self.hud_image,
                             (self.hud_sections_start[i], HEIGHT),
                             (0, 0, self.hud_sections_width[i], FULL_HUB_HEIGHT))
        # test block with
        # pg.draw.rect(self.game.screen, 'green', (self.hud_sections_start[0], HEIGHT - 75, self.hud_sections_width[0], FULL_HUB_HEIGHT- 550))



    def draw_section_text(self, index, message):
        padding_bottom = (HUD_HEIGHT * 1 / 3)
        text = self.text_font.render(f'{message}', True, 'white')
        self.screen.blit(text,
                         (self.hud_sections_start[index] + (self.hud_sections_width[index] - text.get_width()) // 2,
                          FULL_HEIGHT - padding_bottom))
        return text

    def draw_ammo(self):
        self.draw_section_text(2, self.game.weapon.ammo)
        self.draw_section_text(1, 'AMMO')

        ammo = str(self.game.weapon.ammo)
        for i, char in enumerate(ammo):
            # todo params -> (image, (width, height), Rect( (left, top), (width, height)) )
            image = self.digits[char]
            padding = (image.get_width() // 2) * len(ammo)
            self.screen.blit(image,
                             (i * self.digit_size + (self.hud_sections_start[1] + (self.hud_sections_width[1] // 2) - padding), HEIGHT + self.hud_padding_top),
                             (0, 0, self.hud_sections_width[1], FULL_HUB_HEIGHT))

    def draw_player_health_x(self):
        padding_left = 10
        health = str(self.game.player.health)
        for i, char in enumerate(health):
            self.screen.blit(self.digits[char],
                             (i * self.digit_size + self.hud_sections_start[2] + padding_left, HEIGHT + self.hud_padding_top),
                             (0, 0, self.hud_sections_width[2], FULL_HUB_HEIGHT))
        self.screen.blit(self.digits['10'],
                         ((i + 1) * self.digit_size + self.hud_sections_start[2] + padding_left, HEIGHT + self.hud_padding_top),
                         (0, 0, self.hud_sections_width[2], FULL_HUB_HEIGHT))

        self.draw_section_text(2, 'HEALTH')

    def draw_player_health(self):
        padding = 0
        health = str(self.game.player.health)
        percent_image = self.digits['10']
        for i, char in enumerate(health):
            image = self.digits[char]
            padding = ((image.get_width() // 2) * len(health)) + (percent_image.get_width() // 2)
            self.screen.blit(image,
                             (i * self.digit_size + (self.hud_sections_start[2] + (self.hud_sections_width[2] // 2) - padding), HEIGHT + self.hud_padding_top),
                             (0, 0, self.hud_sections_width[2], FULL_HUB_HEIGHT))
        self.screen.blit(percent_image,
                         ((i + 1) * self.digit_size + (self.hud_sections_start[2] + (self.hud_sections_width[2] // 2) - padding), HEIGHT + self.hud_padding_top),
                         (0, 0, self.hud_sections_width[2], FULL_HUB_HEIGHT))

        self.draw_section_text(2, 'HEALTH')


    def draw_arms_digits(self, y, digits):
        # todo params -> (image, (width, height), Rect( (left, top), (width, height)) )`
        start_left = self.hud_sections_width[3] / 1/6
        x = 0
        for i in range(0, 3):
            self.screen.blit(self.arms_image,
                             (self.hud_sections_start[3] + start_left + x, HEIGHT + y),
                             (1, 5, 25, 25))

            if len(self.game.player.weapon_bag) and digits[i] == self.game.player.active_weapon_id:
                color = 'yellow'
            else:
                color = 'lightgray'

            text = self.arms_font.render(f'{digits[i]}', True, color)
            self.screen.blit(text,
                             (self.hud_sections_start[3] + start_left + x + 10, HEIGHT + y + 5))
            x += 30

    def draw_arms(self):
        self.draw_arms_digits(5, [1,2,3])
        self.draw_arms_digits(35, [4,5,6])
        self.draw_section_text(3, 'ARMS')

    def draw_face(self):
        test = self.game.player.health - 90
        idx = ((round(test / 10.0) * 10) // 10)
        self.screen.blit(self.face_image[idx],
                         (self.hud_sections_start[4] + 55, (FULL_HEIGHT - HUD_HEIGHT) + 10),
                         (1, 5, self.face_images[0].get_width(), self.face_images[0].get_height()))

    def draw_armor(self):
        self.draw_section_text(5, 'ARMOR')

    def draw_cards(self):
        pass

    def draw_inventory(self):
        self.draw_section_text(7, 'INVENTORY')






