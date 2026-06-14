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
from drowning_tides.ui.pause_menu import PauseMenu
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
        self.paused = False
        self.pause_menu = PauseMenu(self)

        # grab the mouse for camera look (released while the console/pause menu is open)
        self._set_mouse_capture(True)

    def _set_mouse_capture(self, on):
        pg.mouse.set_visible(not on)
        pg.event.set_grab(on)
        pg.mouse.get_rel()  # drop the accumulated delta so re-capturing doesn't jump

    def _refresh_capture(self):
        # mouse is captured for camera look only while actively playing
        self._set_mouse_capture(not self.console.active and not self.paused)

    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_menu.active = self.paused
        self.pause_menu._dirty = True
        self._refresh_capture()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            elif event.type == pg.KEYDOWN:
                if event.key == cfg.KEYS['CONSOLE']:
                    self.console.toggle()
                    self._refresh_capture()
                elif self.console.active:
                    self.console.handle_key(event)
                    self._refresh_capture()
                elif event.key == cfg.KEYS['FULLSCREEN']:
                    pg.display.toggle_fullscreen()
                elif event.key == cfg.KEYS['QUIT']:
                    self.toggle_pause()
            elif event.type == pg.MOUSEBUTTONDOWN and self.paused:
                if event.button == 1:
                    action = self.pause_menu.click(pg.mouse.get_pos())
                    if action == 'resume':
                        self.toggle_pause()
                    elif action == 'quit':
                        self.quit()
            elif event.type == pg.MOUSEMOTION and not self.console.active and not self.paused:
                self.camera.add_look(*event.rel)
            elif event.type == pg.MOUSEWHEEL and not self.console.active and not self.paused:
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
        self.pause_menu.render()
        pg.display.flip()

    def run(self):
        while True:
            self.handle_events()
            if not self.paused:
                self.update()
                self.time += self.delta_time
            self.render()
            # clamp dt so a long pause (or hitch) doesn't jump the sim on resume
            self.delta_time = min(self.clock.tick(60) / 1000.0, 0.1)


def main():
    Game().run()


if __name__ == '__main__':
    main()
