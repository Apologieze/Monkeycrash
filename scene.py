import launcher
import crash

class Scene():
    def change_scene(self,nb):
        self.current_scene = self.scenes[nb-1]
        self.current_scene.init()

    def __init__(self):
        self.scenes = [launcher, crash]
        self.change_scene(1)
        while True:
            if not self.current_scene.gen.CHANGESCENE:
                self.current_scene.gen.update()
            else:
                self.current_scene.pg.quit()
                self.change_scene(self.current_scene.gen.CHANGESCENE)

Scene()