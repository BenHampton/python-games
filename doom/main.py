from game import *
from sound import *

SCREEN = pg.display.set_mode((WIDTH, FULL_HEIGHT))
SHOW_MENU = False

class InitGame:
    def __init__(self, screen):
        self.screen = screen
        self.init_game()

    def init_game(self):
        self.menu = Menu(self, self.screen)

    def update(self):
        self.menu.update()
        pg.display.flip()

    def draw(self):
        self.menu.draw()

    def check_events(self):
        self.menu.check_for_event()

    def run(self):
        while not self.menu.start_game:
            self.check_events()
            self.update()
            self.draw()

def start_game(level=0):
    game = Game(SCREEN, level)
    game.run()

if __name__ == '__main__':
    pg.init()
    if SHOW_MENU: #for testing to avoid displaying when developing
        init_game = InitGame(SCREEN)
        init_game.run()
        if init_game.menu.start_game:
            start_game(init_game.menu.level)
    else:
        start_game()