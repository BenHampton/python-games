from settings import *
from doom_opengl.meshes.level_mesh import LevelMesh

class Scene:
    def __init__(self, app):
        self.app = app
        self.level_mesh = LevelMesh(self.app)

    def update(self):
        pass

    def render(self):
        self.level_mesh.render()