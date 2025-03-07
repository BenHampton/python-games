import sys
from button import Button
from ground_weapon import GroundWeapon
from ammo import Ammo
from map import *
from hud import *
from object_handler import *
from object_renderer import *
from pathfinding import *
from player import *
from raycasting import *
from sound import *
from weapon import *
from utils.utility import Utility


SCREEN = pg.display.set_mode((WIDTH, FULL_HEIGHT))

SHOW_MENU = False
IS_TEST = False # True/2D mode - False/3D mode

class Game:
    def __init__(self):
        pg.mouse.set_visible(False)

        # todo find a better way to toggle 2D/3D mode
        self.test_mode = False
        self.npc_disabled = True
        self.sound_disabled = True #IS_TEST

        self.screen = SCREEN
        self.current_level = 0
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0
        pg.time.set_timer(self.global_event, 40)

        self.new_game()

    def new_game(self):
        self.map = Map(self)
        self.player = Player(self)
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)
        self.object_handler = ObjectHandler(self)
        self.ground_weapon = GroundWeapon(self)
        self.ammo = Ammo(self)
        self.sound = Sound(self)
        self.pathfinding = PathFinding(self)
        self.hud = Hud(self)

        init_weapon = self.player.weapon_bag[0]
        self.weapon = init_weapon
        self.player.active_weapon = init_weapon

    def next_level(self):
        self.current_level += 1
        self.new_game()

    def completed_game_results(self):
        # todo show game results
        # self.screen.fill('black')
        pass

    def update(self):
        self.player.update()
        self.raycasting.update()
        self.object_handler.update()
        self.hud.update()
        if self.weapon is not None:
            self.weapon.update()

        pg.display.flip()
        self.delta_time = self.clock.tick(FPS)
        pg.display.set_caption(f'{self.clock.get_fps() :.1f}')

    def draw(self):
        if self.test_mode:
            self.screen.fill('black')
            self.map.draw_for_test()
            self.player.draw_for_test()
        else:
            # pg.draw.(self.game.screen, 'blue', (100 * next_x, 100 * next_y, 100, 100))
            self.object_renderer.draw()
            if self.weapon is not None:
                self.weapon.draw()
            self.hud.draw()

    def check_events(self):
        self.global_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            elif event.type == self.global_event:
                self.global_trigger = True
            if self.weapon is not None:
                self.player.fire_weapon_event(event)
            self.player.change_weapon_event(event)

    def run(self):
        while True:
            self.check_events()
            self.update()
            self.draw()

def menu_start_game():
    game = Game()
    if game.sound and not game.sound_disabled:
        game.sound.theme.play()
    game.run()

def menu():
    pg.display.set_caption("Menu")
    bg = pg.image.load('resources/textures/menu/background.png').convert_alpha()

    while True:
        SCREEN.blit(bg, (0, 0))
        menu_mouse_pos = pg.mouse.get_pos()
        menu_text = Utility.get_font('doom.ttf', 100).render("MAIN MENU", True, "white")
        menu_rect = menu_text.get_rect(center=((WIDTH // 2) + 15, 100))
        image = pg.image.load("resources/textures/menu/item_bg_rect.png")

        play_button = Button(image,
                             pos=(50, FULL_HEIGHT - (HUD_HEIGHT // 2) + 10),
                             text_input="PLAY")

        option_button = Button(image,
                               pos=((WIDTH // 2) - (menu_text.get_width() // 2) - 32, FULL_HEIGHT - (HUD_HEIGHT // 2) + 10),
                               text_input="OPTIONS")

        quit_button = Button(image,
                             pos=(WIDTH - image.get_width() - 50, FULL_HEIGHT - (HUD_HEIGHT // 2) + 10),
                             text_input="QUIT")

        SCREEN.blit(menu_text, menu_rect)

        for button in [play_button, option_button, quit_button]:
            button.changeColor(menu_mouse_pos)
            button.update(SCREEN)

        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                if play_button.checkForInput(menu_mouse_pos):
                    menu_start_game()
                if option_button.checkForInput(menu_mouse_pos):
                    print('TODO')
                if quit_button.checkForInput(menu_mouse_pos):
                    pg.quit()
                    sys.exit()

        pg.display.update()

if __name__ == '__main__':
    pg.init()
    if SHOW_MENU: #for testing to avoid displaying when developing
        menu()
    else:
        game = Game()
        if not game.sound_disabled:
            game.sound.theme.play()
        game.run()