import pygame as pg
from settings import *
from utils.utility import Utility

class ObjectRenderer:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.wall_textures = self.load_wall_textures()
        self.sky_image = self.get_texture('resources/textures/sky/' + str(self.game.current_level) + '.png', (WIDTH, HALF_HEIGHT))
        self.sky_offset = 0

        self.font =  Utility.get_font('doom.ttf', 150)

        self. blood_screen = self.get_texture('resources/textures/blood_screen.png', RES)

        self.mission_completed = self.get_texture('resources/textures/mission_completed.png', RES)
        self.win_image = self.get_texture('resources/textures/win.png', RES)
        self.game_over_image = self.get_texture('resources/textures/game_over.png', RES)

    def draw(self):
        self.draw_background()
        self.render_game_objects()

    def draw_text(self, message):
        text = self.font.render(f'{message}', True, 'white')
        self.screen.blit(text,
                         (HALF_WIDTH - text.get_width() // 2,
                          HALF_HEIGHT - text.get_height() // 2))

    def level_completed(self):
        self.draw_text('Mission Completed')

    def win(self):
        self.screen.blit(self.win_image, (0, 0))

    def game_over(self):
        self.screen.blit(self.game_over_image, (0, 0))

    def player_damage(self):
        self.screen.blit(self.blood_screen, (0, 0))

    def draw_background(self):
        #sky
        self.sky_offset = (self.sky_offset + 4.0 * self.game.player.rel) % WIDTH
        self.screen.blit(self.sky_image, (-self.sky_offset, 0))
        self.screen.blit(self.sky_image, (-self.sky_offset + WIDTH, 0))
        # floor
        pg.draw.rect(self.screen, FLOOR_COLOR, (0, HALF_HEIGHT, WIDTH, HEIGHT))
        # pg.draw.rect(self.screen, 'yellow', (self.game.ground_weapon.x, HALF_HEIGHT, self.game.ground_weapon.y * 100 - self.game.ground_weapon.images[0].get_width(), HEIGHT))

    def render_game_objects(self):
        pass
        list_objects = sorted(self.game.raycasting.objects_to_render, key=lambda t: t[0], reverse=True)
        # list_objects = self.game.raycasting.objects_to_render
        for depth, image, pos in list_objects:
            self.screen.blit(image, pos)

    @staticmethod
    def get_texture(path, res=(TEXTURE_SIZE, TEXTURE_SIZE)):
        texture = pg.image.load(path).convert_alpha()
        return pg.transform.scale(texture, res)

    def load_wall_textures(self):
        return {
            1: self.get_texture('resources/textures/wall/gray_brick.png'),
            2: self.get_texture('resources/textures/wall/red_brick.png'),
            3: self.get_texture('resources/textures/wall/gray_moss_brick.png'),
            4: self.get_texture('resources/textures/wall/gray_horn_face.png'),
            5: self.get_texture('resources/textures/wall/red_bird_flag.png'),
            6: self.get_texture('resources/textures/wall/green_brick.png'),
            7: self.get_texture('resources/textures/wall/green_skulls.png'),
            8: self.get_texture('resources/textures/wall/door.png'),
        }

