import sys

from ground_weapon import GroundWeapon
from doom.hud import Hud
from map import *
from hud import *
from object_handler import *
from object_renderer import *
from pathfinding import *
from player import *
from raycasting import *
from sound import *
from weapon import *
from inventory import *

class Game:
    def __init__(self):
        pg.init()
        pg.mouse.set_visible(False)

        # todo find a better way to toggle 2D/3D mode
        is_test = False  # True/2D mode - False/3D mode
        # self.test_mode = True
        self.test_mode = False
        self.npc_disabled = True
        self.sound_disabled = True

        self.new_weapon = None

        self.screen = pg.display.set_mode((WIDTH, FULL_HEIGHT))
        self.map_level = 0
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0
        pg.time.set_timer(self.global_event, 40)
        self.new_game()

    def new_game(self):
        self.map = Map(self)
        self.player = Player(self)
        # self.inventory = Inventory(self)
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)
        self.object_handler = ObjectHandler(self)
        self.ground_weapon = GroundWeapon(self)
        self.sound = Sound(self)
        self.pathfinding = PathFinding(self)
        self.hud = Hud(self)
        init_weapon = self.player.weapon_bag[0](self)
        self.weapon = init_weapon
        self.player.active_weapon_id = init_weapon.weapon_id

    def next_level(self):
        self.map_level += 1
        self.new_game()

    def completed_game_results(self):
        # todo show game results
        # self.screen.fill('black')
        pass

    def update(self):
        self.player.update()
        self.raycasting.update()
        self.object_handler.update()
        if self.weapon is not None:
            self.weapon.update()
        if self.new_weapon is not None and self.weapon is None:
            self.change_weapon()
        pg.display.flip()
        self.delta_time = self.clock.tick(FPS)
        pg.display.set_caption(f'{self.clock.get_fps() :.1f}')

    def change_weapon(self):
        weapon = self.new_weapon(self)
        self.weapon = weapon
        self.player.active_weapon_id = weapon.weapon_id
        self.new_weapon = None

    def draw(self):
        if self.test_mode:
            self.screen.fill('black')
            self.map.draw()
            self.player.draw()
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

if __name__ == '__main__':
    game = Game()
    if not game.sound_disabled:
        game.sound.theme.play()
    game.run()