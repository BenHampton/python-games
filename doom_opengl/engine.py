from level_map import LevelMap
from player import Player, PlayerAttribs
from scene import Scene
from shader_program import ShaderProgram
from textures import Textures
import pygame as pg

class Engine:
    def __init__(self, app):
        self.app = app
        self.ctx = app.ctx
        self.num_level = 0

        self.textures = Textures(self)
        # self.sound = Sound()

        self.player_attribs = PlayerAttribs()
        self.player: Player = None
        self.shader_program: ShaderProgram = None
        self.scene: Scene = None

        self.level_map: LevelMap = None
        # self.ray_casting: RayCasting = None
        # self.path_finder: PathFinder = None
        self.new_game()

    def new_game(self):
        self.player = Player(self)
        self.shader_program = ShaderProgram(self)
        self.level_map = LevelMap(self)
        #     self, tmx_file=f'level_{self.player_attribs.num_level}.tmx'
        # )
        self.scene = Scene(self)

    def handle_events(self, event):
        self.player.handle_events(event=event)

    def update(self):
        self.player.update()
        self.shader_program.update()
        self.scene.update()

    def render(self):
        self.scene.render()