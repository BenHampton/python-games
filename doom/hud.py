import pygame as pg
from os import listdir
from os.path import isfile, join
from settings import *
from utils.utility import Utility

class Hud:
    ANIMATION_DELAY = 1
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.hud_image = self.game.object_renderer.get_texture('resources/textures/hud/section_background.jpg', (WIDTH, HUD_HEIGHT))
        self.arms_image = self.game.object_renderer.get_texture('resources/textures/hud/arms_background.jpg', (WIDTH, HUD_HEIGHT))

        self.text_font = Utility.get_font('doom.ttf', 35)
        self.arms_font = Utility.get_font('doom.ttf', 18)

        self.digit_size = 40
        self.digit_images = [self.game.object_renderer.get_texture(f'resources/textures/digits/{i}.png', [self.digit_size] * 2)
                             for i in range(11)]
        self.digits = dict(zip(map(str, range(11)), self.digit_images))

        self.face_images = self.load_sprite_sheets("hud", "face", 31, 32)
        self.face_image = self.init_face_imag()
        self.animation_count = 0
        self.animation_time =2000
        self.animation_time_prev = pg.time.get_ticks()
        self.animation_trigger = False

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

    def check_animation_time(self):
        self.animation_trigger = False
        time_now = pg.time.get_ticks()
        if time_now - self.animation_time_prev > self.animation_time:
            self.animation_time_prev = time_now
            self.animation_trigger = True

    def animate(self):
        sprite_sheet_name = self.get_face()
        images = self.face_images[sprite_sheet_name]

        if self.animation_trigger:

            sprite_index = (self.animation_count //
                            self.ANIMATION_DELAY) % len(images)
            self.face_image = images[sprite_index]
            self.animation_count += 1

    def update(self):
        self.check_animation_time()
        self.animate()

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
        self.draw_section_text(1, 'AMMO')

        ammo = str(self.game.weapon.ammo)
        for i, char in enumerate(ammo):
            # todo params -> (image, (width, height), Rect( (left, top), (width, height)) )
            image = self.digits[char]
            padding = (image.get_width() // 2) * len(ammo)
            self.screen.blit(image,
                             (i * self.digit_size + (self.hud_sections_start[1] + (self.hud_sections_width[1] // 2) - padding), HEIGHT + self.hud_padding_top),
                             (0, 0, self.hud_sections_width[1], FULL_HUB_HEIGHT))

    def draw_player_health(self):
        self.draw_section_text(2, 'HEALTH')
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

    def draw_arms_digits(self, y, digits):
        # todo params -> (image, (width, height), Rect( (left, top), (width, height)) )`
        start_left = self.hud_sections_width[3] / 1/6
        x = 0
        for i in range(0, 3):
            self.screen.blit(self.arms_image,
                             (self.hud_sections_start[3] + start_left + x, HEIGHT + y),
                             (1, 5, 25, 25))

            color = 'lightgray'
            if (len(self.game.player.weapon_bag) and self.game.weapon is not None
                    and self.game.player.active_weapon in self.game.player.weapon_bag
                    and digits[i] == self.game.player.active_weapon.weapon_id):
                color = 'yellow'

            text = self.arms_font.render(f'{digits[i]}', True, color)
            self.screen.blit(text,
                             (self.hud_sections_start[3] + start_left + x + 10, HEIGHT + y + 5))
            x += 30

    def draw_arms(self):
        self.draw_arms_digits(5, [1,2,3])
        self.draw_arms_digits(35, [4,5,6])
        self.draw_section_text(3, 'ARMS')

    #todo the image cropping works but looks like its off by a pixel, fix and the update draw_face->(see todo)
    @staticmethod
    def load_sprite_sheets(dir1, dir2, width, height):
        path = join('resources/textures', dir1, dir2)
        images = [f for f in listdir(path) if isfile(join(path, f))]

        all_sprites = {}

        for index, image in enumerate(images):

            sprite_sheet = pg.image.load(join(path, image)).convert_alpha()
            sprite_sheet = pg.transform.scale(sprite_sheet, (90 , height))

            sprites = []
            for i in range(3):
                surface = pg.Surface((width, height), pg.SRCALPHA, 32)
                rect = pg.Rect(i * width + 0, 0, width, height)
                surface.blit(sprite_sheet, (0, 0), rect)
                transform = pg.transform.scale(surface, (120, 80))
                sprites.append(transform)

            all_sprites[image.replace(".png", "")] = sprites
        return all_sprites

    @staticmethod
    def flip(sprites):
        return [pg.transform.flip(sprite, True, False) for sprite in sprites]

    def init_face_imag(self):
        sprite_sheet_name = self.get_face()
        images = self.face_images[sprite_sheet_name]
        return images[1]

    def get_face(self):
        health = self.game.player.health
        if health > 91:
            sprite_sheet = "great"
        elif health > 71:
            sprite_sheet = "good"
        elif health > 51:
            sprite_sheet = "ok"
        elif health > 31:
            sprite_sheet = "not_good"
        else:
            sprite_sheet = "bad"
        return sprite_sheet

    #todo fix load_sprite_sheets and remove the '+ 5' in this method (used for centering)
    def draw_face(self):
        self.screen.blit(self.face_image,
                         (self.hud_sections_start[4] + (self.hud_sections_width[4] // 2) - (self.face_image.get_width() // 2) + 5,
                          FULL_HUB_HEIGHT + 15),
                         (1, 5, self.face_image.get_width(), self.face_image.get_height()))
        # pg.draw.rect(self.game.screen, 'green',
        #              (self.hud_sections_start[4] + (self.hud_sections_width[4] // 2) - (self.face_image.get_width() // 2), FULL_HUB_HEIGHT + 10 - 75,
        #               self.face_image.get_width(), self.face_image.get_height()))


    def draw_armor(self):
        self.draw_section_text(5, 'ARMOR')

    def draw_cards(self):
        pass

    def draw_inventory(self):
        self.draw_section_text(7, 'INVENTORY')






