import launcher
import crash
import coinflip
import pygame as pg

class Scene():
    """Scene Manager that allows you to easily navigate between the different games and the launcher"""
    def change_scene(self,nb):
        self.current_scene = self.scenes[nb-1]
        self.current_scene.init(self.res, self.FULLSCREEN)

    def __init__(self):
        pg.init()
        self.scenes = [launcher, crash, coinflip]
        self.FULLSCREEN = False
        self.res = [(pg.display.Info().current_w, pg.display.Info().current_h),(1200, 800)]
        self.change_scene(1)
        while True:
            if not self.current_scene.gen.CHANGESCENE:
                self.current_scene.gen.update()
            else:
                # self.current_scene.pg.quit()
                self.res = self.current_scene.gen.tempres
                self.FULLSCREEN = self.current_scene.gen.FULLSCREEN
                self.change_scene(self.current_scene.gen.CHANGESCENE)

Scene()