import pygame as pg

class Utility:

    @staticmethod
    def get_font(filename, size):
        text_font = pg.font.Font(f'resources/font/{filename}', size)
        return text_font

