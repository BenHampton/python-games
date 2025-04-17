import pygame as pg
from camera import Camera
from settings import *

class PlayerAttribs:
    def __init__(self):
        self.num_level = 0

    def update(self):
        pass

class Player(Camera):
    def __init__(self, eng, position=PLAYER_POS, yaw=-90, pitch=0):
        self.app = eng.app
        self.eng = eng
        super() .__init__(position, yaw, pitch)

        # these maps will update when instantiated LevelMap
        self.door_map, self.wall_map, self.item_map = None, None, None

        # attribs
        self.health = PLAYER_INIT_HEALTH
        self.ammo = PLAYER_INIT_AMMO
        #
        self.tile_pos: Tuple[int, int] = None

    def update_tile_position(self):
        self.tile_pos = int(self.position.x), int(self.position.z)

    def pick_up_item(self):
        if self.tile_pos not in self.item_map:
            return None

        item = self.item_map[self.tile_pos]
        #
        if item.tex_id == ID.MED_KIT:
            self.health += ITEM_SETTINGS[ID.MED_KIT]['value']
            self.health = min(self.health, MAX_HEALTH_VALUE)
            #
        elif item.tex_id == ID.AMMO:
            self.ammo += ITEM_SETTINGS[ID.AMMO]['value']
            self.ammo = min(self.ammo, MAX_AMMO_VALUE)
        #
        del self.item_map[self.tile_pos]

    def handle_events(self, event):
        if event.type == pg.KEYDOWN:
            #
            if event.key == KEYS['INTERACT']:
                self.interact_with_door()

    def update(self):
        self.keyboard_control()
        self.mouse_control()
        super().update()
        #
        self.update_tile_position()
        self.pick_up_item()

    def interact_with_door(self):
        pos = self.position + self.forward
        int_pos = int(pos.x), int(pos.z)
        #
        if int_pos in self.door_map:
            door = self.door_map[int_pos]
            door.is_moving = True

    def mouse_control(self):
        mouse_dx, mouse_dy = pg.mouse.get_rel()
        if mouse_dx:
            self.rotate_yaw(delta_x=mouse_dx * MOUSE_SENSITIVITY)
        if mouse_dy:
            self.rotate_pitch(delta_y=mouse_dy * MOUSE_SENSITIVITY)

    def keyboard_control(self):
        key_state = pg.key.get_pressed()
        vel = PLAYER_SPEED * self.app.delta_time
        next_step = glm.vec2()
        #
        if key_state[KEYS['FORWARD']]:
            next_step += self.move_forward(vel)
        if key_state[KEYS['BACK']]:
            next_step += self.move_back(vel)
        if key_state[KEYS['STRAFE_R']]:
            next_step += self.move_right(vel)
        if key_state[KEYS['STRAFE_L']]:
            next_step += self.move_left(vel)
        #
        self.move(next_step=next_step)

    # TODO does not work -> why?
    # def keyboard_control_old(self):
    #     key_state = pg.key.get_pressed()
    #     vel = PLAYER_SPEED * self.app.delta_time
    #     next_step = glm.vec2()
    #
    #     if key_state[pg.K_w]:
    #         self.move_forward(vel)
    #     if key_state[pg.K_s]:
    #         self.move_back(vel)
    #     if key_state[pg.K_d]:
    #         self.move_right(vel)
    #     if key_state[pg.K_a]:
    #         self.move_left(vel)
    #     if key_state[pg.K_q]:
    #         self.move_up(vel)
    #     if key_state[pg.K_e]:
    #         self.move_down(vel)
    #     #
    #     self.move(next_step-next_step)

    def move(self, next_step):
        if not self.is_collide(dx=next_step[0]):
            self.position.x += next_step[0]

        if not self.is_collide(dz=next_step[1]):
            self.position.z += next_step[1]

    def is_collide(self, dx=0, dz=0):
        int_pos = (
            int(self.position.x + dx + (
                PLAYER_SIZE if dx > 0 else -PLAYER_SIZE if dx < 0 else 0)
                ),
            int(self.position.z + dz + (
                PLAYER_SIZE if dz > 0 else -PLAYER_SIZE if dz < 0 else 0)
                )
        )
        # check doors
        if int_pos in self.door_map:
            return self.door_map[int_pos].is_closed

        return int_pos in self.wall_map