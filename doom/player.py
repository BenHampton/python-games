import pygame as pg

from weapon import PistolWeapon, ShotgunWeapon, AxeWeapon
from settings import *
import math

class Player:
    def __init__(self, game):
        self.game = game
        self.x, self.y = PLAYER_POS
        self.angle = PLAYER_ANGLE
        self.shot = False
        self.health = PLAYER_MAX_HEALTH
        self.rel = 0
        self.health_recovery_delay = 700
        self.time_prev = pg.time.get_ticks()
        self.weapon_bag = []
        self.active_weapon_id = -1

    def recover_health(self):
        if self.check_health_recovery_delay() and self.health < PLAYER_MAX_HEALTH:
            self.health += 1

    def check_health_recovery_delay(self):
        time_now = pg.time.get_ticks()
        if time_now - self.time_prev > self.health_recovery_delay:
            self.time_prev = time_now
            return True

    def check_game_over(self):
        if self.health < 1:
            self.game.object_renderer.game_over()
            pg.display.flip()
            pg.time.delay(1500)
            self.game.new_game()

    def get_damage(self, damage):
        self.health -= damage
        self.game.object_renderer.player_damage()
        if not self.game.sound_disabled:
            self.game.sound.player_pain.play()
        self.check_game_over()

    def single_fire_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1 and not self.shot and not self.game.weapon.reloading:
                if not self.game.sound_disabled:
                    self.game.sound.shotgun.play()
                self.shot = True
                self.game.weapon.reloading = True

    def change_weapon_event(self, event):
        new_weapon = None
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_1:
               new_weapon = PistolWeapon
            if event.key == pg.K_2:
                new_weapon = ShotgunWeapon
            if event.key == pg.K_3:
                new_weapon = AxeWeapon
            if new_weapon is not None:
                print(str(new_weapon))
                print(str(self.weapon_bag))
                for i in self.weapon_bag:
                    if i == new_weapon:
                        self.game.new_weapon = new_weapon
                        self.game.weapon = None

    def movement(self):
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)
        dx, dy = 0, 0
        # if we want the player's movement speed to be independent of the frame rate
        # then we need to get the delta time value for each frame
        speed = PLAYER_SPEED * self.game.delta_time
        speed_sin = speed * sin_a
        speed_cos = speed * cos_a

        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            dx += speed_cos
            dy += speed_sin
        if keys[pg.K_s]:
            dx += -speed_cos
            dy += -speed_sin
        if keys[pg.K_a]:
            dx += speed_sin
            dy += -speed_cos
        if keys[pg.K_d]:
            dx += -speed_sin
            dy += speed_cos

        # self.x += dx
        # self.y += dy
        # instead of changing the player coords use method to enable wall collision
        self.check_wall_collision(dx, dy)

        # player movement with arrow keys in favor of mouse movement
        # if keys[pg.K_LEFT]:
        #     self.angle -= PLAYER_ROT_SPEED * self.game.delta_time
        # if keys[pg.K_RIGHT]:
        #     self.angle += PLAYER_ROT_SPEED * self.game.delta_time

        # tau = 2*pi
        self.angle %= math.tau

    def check_wall(self, x, y):
        return (x, y) not in self.game.map.world_map

    def check_wall_collision(self, dx, dy):
        scale = PLAYER_SIZE_SCALE / self.game.delta_time
        if self.check_wall(int(self.x + dx * scale), int(self.y)):
            self.x += dx
        if self.check_wall(int(self.x), int(self.y + dy * scale)):
            self.y += dy

    # test player, test his direction of movement as a line an the player as a circle
    def draw(self):
        if self.game.test_mode:
            pg.draw.line(self.game.screen,
                         'yellow',
                         (self.x * 100, self.y * 100),
                         (self.x * 100 + WIDTH * math.cos(self.angle), self.y * 100 + WIDTH * math.sin(self.angle)),
                         2)
            pg.draw.rect(self.game.screen, 'pink', (self.x * 100 - 50, self.y * 100 - 50, 100, 100), 2)
            pg.draw.circle(self.game.screen, 'green', (self.x * 100, self.y * 100), 15)

    def mouse_control(self):
        mx, my = pg.mouse.get_pos()
        if mx < MOUSE_BORDER_LEFT or mx > MOUSE_BORDER_RIGHT:
            pg.mouse.set_pos([HALF_WIDTH, HALF_HEIGHT])
        self.rel = pg.mouse.get_rel()[0]
        self.rel = max(-MOUSE_MAX_REL, min(MOUSE_MAX_REL, self.rel))
        self.angle += self.rel * MOUSE_SENSITIVITY * self.game.delta_time

    def update(self):
        self.movement()
        self.mouse_control()
        self.recover_health()

    @property
    def pos(self):
        return self.x, self.y

    @property
    def map_pos(self):
        return int(self.x), int(self.y)