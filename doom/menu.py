import pygame as pg
import sys

from doom.map import MAPS
from settings import *
from utils.utility import Utility
from button import Button

class Menu:
    def __init__(self, init_game, screen):
        self.init_game = init_game
        self.init_game.screen = screen
        self.level = 0
        self.menu_mouse_pos = pg.mouse.get_pos()

        self.menu_text = Utility.get_font('doom.ttf', 100).render("Main Menu", True, "white")
        self.menu_rect = self.menu_text.get_rect(center=((WIDTH // 2) + 15, 100))

        self.map_image_size = 100
        self.map_images = [
            self.get_texture(f'resources/textures/menu/map_options/{i}.png', (WIDTH - 450, HEIGHT - HUD_HEIGHT - 100))
            for i in range(len(MAPS))]
        self.map_image = dict(zip(map(str, range(len(MAPS))), self.map_images))
        self.selected_map_image_index = 0

        self.start_game = False
        self.play_button = None
        self.option_button = None
        self.quit_button = None

        self.map_option_button_right = None
        self.map_option_button = None
        self.map_option_button_left = None
        self.back_button = None

        self.is_menu_section = True
        self.is_map_option_section = False

    def update(self):
        self.menu_mouse_pos = pg.mouse.get_pos()

    def draw(self):
        self.draw_background()
        if self.is_menu_section:
            self.draw_menu()
        elif self.is_map_option_section:
            self.draw_menu_options()

    def check_for_event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                if self.is_menu_section:
                    self.check_for_menu_event()
                if self.is_map_option_section:
                    self.check_for_map_option_event()

    def check_for_menu_event(self):
        if self.play_button is not None and self.play_button.checkForInput(self.menu_mouse_pos):
            self.start_game = True
        if self.option_button is not None and self.option_button.checkForInput(self.menu_mouse_pos):
            self.reset_buttons()
            self.is_menu_section = False
            self.is_map_option_section = True
        if self.quit_button is not None and self.quit_button.checkForInput(self.menu_mouse_pos):
            pg.quit()
            sys.exit()

    def check_for_map_option_event(self):
        if self.map_option_button_right is not None and self.map_option_button_right.checkForInput(self.menu_mouse_pos):
            self.handle_map_option_event_right()
        if self.map_option_button is not None and self.map_option_button.checkForInput(self.menu_mouse_pos):
            self.handle_map_option_event()
        if self.map_option_button_left is not None and self.map_option_button_left.checkForInput(self.menu_mouse_pos):
            self.handle_map_option_event_left()
        if self.back_button is not None and self.back_button.checkForInput(self.menu_mouse_pos):
            self.reset_buttons()
            self.is_map_option_section = False
            self.is_menu_section = True

    def handle_map_option_event_right(self):
        if self.selected_map_image_index == 0:
            self.selected_map_image_index = len(self.map_images) - 1
        else:
            self.selected_map_image_index -= 1

    def handle_map_option_event(self):
        self.level = self.selected_map_image_index
        self.start_game = True

    def handle_map_option_event_left(self):
        if self.selected_map_image_index == len(self.map_images) - 1:
            self.selected_map_image_index = 0
        else:
            self.selected_map_image_index += 1

    def reset_buttons(self):
        self.play_button = None
        self.option_button = None
        self.quit_button = None

        self.map_option_button_right = None
        self.map_option_button = None
        self.map_option_button_left = None
        self.back_button = None


    def draw_background(self):
        bg = pg.image.load('resources/textures/menu/background.png').convert_alpha()
        self.init_game.screen.blit(bg, (0, 0))

    def draw_menu(self):
        pg.display.set_caption("Menu")
        self.init_game.screen.blit(self.menu_text, self.menu_rect)
        image = pg.image.load("resources/textures/menu/item_bg_rect.png")

        self.play_button = Button(image,
                             pos=(50, FULL_HEIGHT - (HUD_HEIGHT // 2) + 10),
                             text_input="PLAY")

        self.option_button = Button(image,
                               pos=((WIDTH // 2) - (self.menu_text.get_width() // 2) - 32,
                                    FULL_HEIGHT - (HUD_HEIGHT // 2) + 10),
                               text_input="MAPS")

        self.quit_button = Button(image,
                             pos=(WIDTH - image.get_width() - 50, FULL_HEIGHT - (HUD_HEIGHT // 2) + 10),
                             text_input="QUIT")

        self.init_game.screen.blit(self.menu_text, self.menu_rect)

        for button in [self.play_button, self.option_button, self.quit_button]:
            button.changeColor(self.menu_mouse_pos)
            button.update(self.init_game.screen)

    @staticmethod
    def get_texture(path, res=(TEXTURE_SIZE, TEXTURE_SIZE)):
        texture = pg.image.load(path).convert_alpha()
        return pg.transform.scale(texture, res)

    def draw_menu_options(self):
        self.menu_text = Utility.get_font('doom.ttf', 100).render('MAP OPTIONS', True, "white")
        self.menu_rect = self.menu_text.get_rect(center=((WIDTH // 2) + 15, 100))
        self.init_game.screen.blit(self.menu_text, self.menu_rect)

        btn_image = pg.image.load("resources/textures/menu/item_bg_rect.png")

        self.back_button = Button(btn_image, pos=(25, HALF_HEIGHT - 225), text_input='Back')

        # todo params -> (image, (width, height), Rect( (left, top), (width, height)) )
        map_img = self.map_images[self.selected_map_image_index]
        self.init_game.screen.blit(map_img,
                         ((WIDTH // 2) - (map_img.get_width() // 2), (FULL_HEIGHT // 2) - (map_img.get_height() // 2) - 10),
                         (0, 0, map_img.get_width(), map_img.get_height()))

        self.map_option_button_right = Button(btn_image,
                                              pos=(50, FULL_HEIGHT - (HUD_HEIGHT // 2) + 10),
                                              text_input='<')

        self.map_option_button = Button(btn_image,
                                        pos=(HALF_WIDTH - (btn_image.get_width() // 2), FULL_HEIGHT - (HUD_HEIGHT // 2) + 10),
                                        text_input='Select Level ' + str(self.selected_map_image_index + 1))

        self.map_option_button_left = Button(btn_image,
                                             pos=(WIDTH - 50 - btn_image.get_width(), FULL_HEIGHT - (HUD_HEIGHT // 2) + 10),
                                             text_input='>')

        for button in ([self.map_option_button_right, self.map_option_button, self.map_option_button_left, self.back_button]):
            button.changeColor(self.menu_mouse_pos)
            button.update(self.init_game.screen)

