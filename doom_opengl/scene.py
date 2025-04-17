from doom_opengl.game_objects.hud import HUD
from meshes.instanced_quad_mesh import InstancedQuadMesh
from settings import *
from meshes.level_mesh import LevelMesh

class Scene:
    def __init__(self, eng):
        self.eng = eng

        # level mesh
        self.level_mesh = LevelMesh(self.eng)

        self.hud = HUD(eng)

        # door objects
        self.doors = self.eng.level_map.door_map.values()
        self.items = self.eng.level_map.item_map.values()

        # door mesh
        self.instanced_door_mesh = InstancedQuadMesh(
            self.eng, self.doors, self.eng.shader_program.instanced_door
        )
        # item mesh
        self.instanced_item_mesh = InstancedQuadMesh(
            self.eng, self.items, self.eng.shader_program.instanced_billboard
        )
        # hud mesh
        self.instanced_hud_mesh = InstancedQuadMesh(
            eng, self.hud.objects, eng.shader_program.instanced_hud
        )

    def update(self):
        for door in self.doors:
            door.update()
        self.hud.update()

    def render(self):
        self.level_mesh.render()
        self.instanced_door_mesh.render()
        self.instanced_item_mesh.render()
        self.instanced_hud_mesh.render()