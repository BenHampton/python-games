import sys

import moderngl as mgl
import pygame as pg
from pyglm import glm

from drowning_tides.config import settings as cfg
from drowning_tides.core.game_state import GameState
from drowning_tides.core.shader_program import ShaderProgram
from drowning_tides.render.camera import Camera
from drowning_tides.render.scene import Scene
from drowning_tides.ui.console import Console
from drowning_tides.world.boat import Boat
from drowning_tides.world.daycycle import DayCycle
from drowning_tides.world.island import IslandField
from drowning_tides.world.waves import WaveField
from drowning_tides.world.weather import Weather


class Game:
    def __init__(self):
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, cfg.MAJOR_VERSION)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, cfg.MINOR_VERSION)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.gl_set_attribute(pg.GL_DEPTH_SIZE, cfg.DEPTH_SIZE)

        flags = pg.OPENGL | pg.DOUBLEBUF
        if cfg.FULLSCREEN:
            info = pg.display.Info()
            win_w, win_h = info.current_w, info.current_h
            flags |= pg.FULLSCREEN
        else:
            win_w, win_h = int(cfg.WIN_RES.x), int(cfg.WIN_RES.y)
        pg.display.set_mode((win_w, win_h), flags=flags)
        pg.display.set_caption('Drowning Tides')

        # lock the configured resolution + aspect to the actual window (fullscreen native res)
        cfg.WIN_RES = glm.vec2(win_w, win_h)
        cfg.ASPECT_RATIO = win_w / win_h

        self.ctx = mgl.create_context()
        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.BLEND)
        self.ctx.gc_mode = 'auto'

        self.clock = pg.time.Clock()
        self.delta_time = 0.0
        self.time = 0.0

        # control mode (HELM by default; ON_FOOT lands with the mount/unmount phase)
        self.game_state = GameState()
        self.daycycle = DayCycle()

        # init order: weather/waves -> shaders -> boat -> console -> camera -> scene
        self.weather = Weather()
        self.wave_field = WaveField()
        self.shader_program = ShaderProgram(self)
        self.islands = IslandField(self)
        self.shader_program.set_shallows(self.islands.islands)
        self.boat = Boat(self)
        self.console = Console(self)
        self.camera = Camera(self)
        self.scene = Scene(self)

        # grab the mouse for camera look (released while the console is open)
        self._set_mouse_capture(True)

    def _set_mouse_capture(self, on):
        pg.mouse.set_visible(not on)
        pg.event.set_grab(on)
        pg.mouse.get_rel()  # drop the accumulated delta so re-capturing doesn't jump

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            elif event.type == pg.KEYDOWN:
                if event.key == cfg.KEYS['CONSOLE']:
                    self.console.toggle()
                    self._set_mouse_capture(not self.console.active)
                elif self.console.active:
                    self.console.handle_key(event)
                elif event.key == cfg.KEYS['QUIT']:
                    self.quit()
            elif event.type == pg.MOUSEMOTION and not self.console.active:
                self.camera.add_look(*event.rel)
            elif event.type == pg.MOUSEWHEEL and not self.console.active:
                self.camera.zoom(event.y)

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        self.weather.update(self.delta_time)
        self.daycycle.update(self.delta_time)
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
