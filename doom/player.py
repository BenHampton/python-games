﻿import pygame as pg
from weapon import PistolWeapon, ShotgunWeapon, AxeWeapon, ChaingunWeapon, PlasmaRifleWeapon, BFGWeapon
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
        self.active_weapon = None
        #todo update weapon_key_map to dynamically set keys to Weapon class
        self.weapon_key_map = {pg.K_1: PistolWeapon,
                               pg.K_2: ShotgunWeapon,
                               pg.K_3: AxeWeapon,
                               pg.K_4: ChaingunWeapon,
                               pg.K_5: PlasmaRifleWeapon,
                               pg.K_6: BFGWeapon}

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

    #todo move weapon sound to weapon.py
    def fire_weapon_event(self, event):
        if self.game.weapon.is_automatic:
            self.automatic_fire_event(event)
        else:
            self.single_fire_event(event)

    def automatic_fire_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1 and not self.shot and not self.game.weapon.reloading:
                if not self.game.sound_disabled:
                    self.game.sound.shotgun.play()
                self.shot = True
        if event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                self.shot = False

    def single_fire_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1 and not self.shot and not self.game.weapon.reloading:
                if not self.game.sound_disabled:
                    self.game.sound.shotgun.play()
                self.shot = True
                self.game.weapon.reloading = True

    def change_weapon_event(self, event):
        if event.type == pg.KEYDOWN:
            weapon_key = self.weapon_key_map.get(event.key)
            if weapon_key is not None:
                for wb in self.weapon_bag:
                    if wb.weapon_id == weapon_key(self.game).weapon_id:
                        self.game.weapon = wb
                        self.game.player.active_weapon = wb

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
        if keys[pg.K_e] and self.game.door.active_door_coords is not None:
            self.game.map.handle_open_door(self.game.door.active_door_coords)

        # self.x += dx
        # self.y += dy
        # instead of changing the player coords use method to enable wall collision
        self.check_collision(dx, dy)

        # player movement with arrow keys in favor of mouse movement
        # if keys[pg.K_LEFT]:
        #     self.angle -= PLAYER_ROT_SPEED * self.game.delta_time
        # if keys[pg.K_RIGHT]:
        #     self.angle += PLAYER_ROT_SPEED * self.game.delta_time

        # tau = 2*pi
        self.angle %= math.tau

    def check_wall(self, x, y):
        return (x, y) not in self.game.map.world_map

    def check_wall_collision(self, dx, dy, scale):
        if self.check_wall(int(self.x + dx * scale), int(self.y)):
            self.x += dx
        if self.check_wall(int(self.x), int(self.y + dy * scale)):
            self.y += dy

    def check_collision(self, dx, dy):
        scale = PLAYER_SIZE_SCALE / self.game.delta_time

        self.check_wall_collision(dx, dy, scale)
        self.game.door.check_door(self.x, self.y, dx, dy, scale)

    def draw_for_test(self):
        if self.game.test_mode:
            dim = TEST_SPAWN_COVERAGE_DIM[self.game.current_level]
            dim_two = dim // 2
            radius = TEST_SPAWN_RADIUS[self.game.current_level]
            pg.draw.line(self.game.screen,'yellow',(self.x * dim, self.y * dim),(self.x * dim + WIDTH * math.cos(self.angle), self.y * dim + WIDTH * math.sin(self.angle)),2)
            pg.draw.rect(self.game.screen, 'green', (self.x * dim - dim_two, self.y * dim - dim_two, dim, dim), 2)
            pg.draw.circle(self.game.screen, 'green', (self.x * dim, self.y * dim), radius)

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