import sys

import moderngl as mgl
import pygame as pg

from drowning_tides.config import settings as cfg
from drowning_tides.core.shader_program import ShaderProgram
from drowning_tides.render.camera import Camera
from drowning_tides.render.scene import Scene
from drowning_tides.ui.console import Console
from drowning_tides.world.boat import Boat
from drowning_tides.world.waves import WaveField
from drowning_tides.world.weather import Weather


class Game:
    def __init__(self):
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, cfg.MAJOR_VERSION)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, cfg.MINOR_VERSION)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.gl_set_attribute(pg.GL_DEPTH_SIZE, cfg.DEPTH_SIZE)

        pg.display.set_mode(
            (int(cfg.WIN_RES.x), int(cfg.WIN_RES.y)), flags=pg.OPENGL | pg.DOUBLEBUF
        )
        pg.display.set_caption('Drowning Tides')

        self.ctx = mgl.create_context()
        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.BLEND)
        self.ctx.gc_mode = 'auto'

        self.clock = pg.time.Clock()
        self.delta_time = 0.0
        self.time = 0.0

        # init order: weather/waves -> shaders -> boat -> console -> camera -> scene
        self.weather = Weather()
        self.wave_field = WaveField()
        self.shader_program = ShaderProgram(self)
        self.boat = Boat(self)
        self.console = Console(self)
        self.camera = Camera(self)
        self.scene = Scene(self)

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == cfg.KEYS['CONSOLE']:
                    self.console.toggle()
                elif self.console.active:
                    self.console.handle_key(event)
                elif event.key == cfg.KEYS['QUIT']:
                    self.quit()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        self.weather.update(self.delta_time)
        self.wave_field.recompute(self.weather.wind_dir, self.weather.storm_intensity)
        self.boat.update(self.delta_time)
        self.camera.update(self.delta_time)
        self.shader_program.update()

    def render(self):
        self.scene.render()
        pg.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.render()
            self.delta_time = self.clock.tick(60) / 1000.0
            self.time += self.delta_time


def main():
    Game().run()


if __name__ == '__main__':
    main()
