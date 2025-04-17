from settings import *
from pyglm import glm
from doom_opengl.game_objects.game_object import GameObject
from doom_opengl.settings import WALL_SIZE, ANIM_DOOR_SPEED


class Door(GameObject):
    def __init__(self, level_map, tex_id, x, z):
        super().__init__(level_map, tex_id, x, z)
        #
        self.rot = self.get_rot(x, z)
        self.m_model = self.get_model_matrix()
        #
        self.is_closed = True
        self.is_moving = False

    def get_rot(self, x, z):
        wall_map = self.level_map.wall_map
        if (x, z - 1) in wall_map and (x, z + 1) in wall_map:
            return glm.half_pi()
        return 0

    def update(self):
        if not self.is_moving:
            return None

        if self.is_closed and self.pos.y < WALL_SIZE - ANIM_DOOR_SPEED:
            if self.app.anim_trigger:
                self.pos.y += ANIM_DOOR_SPEED
                self.m_model = self.get_model_matrix()
        elif not self.is_closed and self.pos.y > 0:
            if self.app.anim_trigger:
                self.pos.y -= ANIM_DOOR_SPEED
                self.m_model = self.get_model_matrix()
        else:
            self.is_moving = False
            self.is_closed = not self.is_closed
