from settings import *
from utils.utility import Utility

class Door:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.active_door_coords = None
        self.font = Utility.get_font('doom.ttf', 50)

    def draw(self):
        if self.active_door_coords is not None:
            text = self.font.render('Press E to open door', True, 'white')
            self.screen.blit(text, (HALF_WIDTH - text.get_width() // 2, 100))

    def check_door(self, x, y, dx, dy, scale):
        self.handle_checking_door(int(x + dx * scale), int(y))
        self.handle_checking_door(int(x), int(y + dy * scale))

    def handle_checking_door(self, x, y):
        door_pos = (x, y) in self.game.map.door_interation_coords
        if door_pos:
            self.active_door_coords = (x, y)
            return True
        else:
            self.active_door_coords = None
            return False
