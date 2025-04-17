from settings import *
from doom_opengl.game_objects.game_object import GameObject


class Door(GameObject):
    def __init__(self, level_map, tex_id, x, z):
        super().__init__(level_map, tex_id, x, z)

        self.m_model = self.get_model_matrix()

    def update(self):
        pass