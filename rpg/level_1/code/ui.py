import pygame
import pygame as pg
from settings import *

class UI:
    def __init__(self):

        #general
        self.display_surface = pg.display.get_surface()
        self.font = pg.font.Font(UI_FONT, UI_FONT_SIZE)

        #bar setup
        self.health_bar_rect = pg.Rect(10, 10, HEALTH_BAR_WIDTH, BAR_HEIGHT)
        self.energy_bar_rect = pg.Rect(10, 34, ENERGY_BAR_WIDTH, BAR_HEIGHT)

        #convert weapon dictionary
        self.weapon_graphics = self.get_combat_item_graphics(weapon_data.values())

        # convert magic dictionary
        self.magic_graphics = self.get_combat_item_graphics(magic_data.values())

    @staticmethod
    def get_combat_item_graphics(data_values):
        graphics = []
        for item_graphic in data_values:
            path = item_graphic['graphic']
            graphic = pygame.image.load(path).convert_alpha()
            graphics.append(graphic)

        return graphics

    def show_bar(self, current, max_amount, bg_rect, color):
        #draw background
        pg.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)

        #convert stat to pixel
        ratio = current / max_amount
        current_width = bg_rect.width * ratio
        current_rect = bg_rect.copy()
        current_rect.width = current_width

        #draw bar
        pg.draw.rect(self.display_surface, color, current_rect)
        pg.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)

    def show_exp(self, exp):
        text_sur = self.font.render(str(int(exp)), False, TEXT_COLOR)
        x = self.display_surface.get_size()[0] - 20
        y = self.display_surface.get_size()[1] - 20
        text_rect = text_sur.get_rect(bottomright=(x, y))

        pg.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(20, 20))
        self.display_surface.blit(text_sur, text_rect)
        pg.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(20, 20), 3)

    def selection_box(self, left, top, has_switched):
        bg_rect = pg.Rect(left, top, ITEM_BOX_SIZE, ITEM_BOX_SIZE)
        pg.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        if has_switched:
            pg.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, bg_rect, 3)

        else:
            pg.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)

        return bg_rect

    def weapon_overlay(self, weapon_index, has_switched):
        bg_rect = self.selection_box(10, 630, has_switched)
        self.combat_item_overlay(bg_rect, self.weapon_graphics, weapon_index)

    def magic_overlay(self, magic_index, has_switched):
        bg_rect = self.selection_box(80, 635, has_switched)
        self.combat_item_overlay(bg_rect, self.magic_graphics, magic_index)

    def combat_item_overlay(self, bg_rect, combat_graphics, combat_item_index):
        combat_surf = combat_graphics[combat_item_index]
        combat_rect = combat_surf.get_rect(center=bg_rect.center)
        self.display_surface.blit(combat_surf, combat_rect)

    def display(self, player):
        self.show_bar(player.health, player.stats['health'], self.health_bar_rect, HEALTH_COLOR)
        self.show_bar(player.energy, player.stats['energy'], self.energy_bar_rect, ENERGY_COLOR)

        self.show_exp(player.exp)

        self.weapon_overlay(player.weapon_index, not player.can_switch_weapon) #weapon
        self.magic_overlay(player.magic_index, not player.can_switch_magic) #magic
