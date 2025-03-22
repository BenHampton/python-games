from map import *
from player import *
from ground_item import *
from hud import *
from object_handler import *
from object_renderer import *
from pathfinding import *
from raycasting import *
from sound import *
from door import *
from menu import *

IS_TEST = False # True/2D mode - False/3D mode

class Game:
    def __init__(self, screen, level):
        pg.mouse.set_visible(False)

        # todo find a better way to toggle 2D/3D mode
        self.test_mode = False
        # self.test_mode = True
        self.npc_disabled, self.npc_disabled_walk = True, True
        self.sound_disabled = True #IS_TEST

        self.screen = screen
        self.current_level = level
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
        self.door = Door(self)
        # self.ground_weapon = GroundWeapon(self)
        # self.ammo = Ammo(self)
        self.ground_item = GroundItem(self)
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
            self.door.draw()

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
            self.change_weapon_event(event)

    def change_weapon_event(self, event):
        if event.type == pg.KEYDOWN:
            weapon_key = self.player.weapon_key_map.get(event.key)
            if weapon_key is not None:
                for weapon_in_bag in self.player.weapon_bag:
                    if isinstance(weapon_in_bag, weapon_key):
                        self.weapon = weapon_in_bag
                        self.player.active_weapon = weapon_in_bag

    def run(self):
        if self.sound and not self.sound_disabled:
            self.sound.theme.play()
        while True:
            self.check_events()
            self.update()
            self.draw()
