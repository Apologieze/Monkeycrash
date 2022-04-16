import pygame as pg
from sys import exit
import ctypes as ct
import json

class Gen:
    def crea(self, tempres, fullscreen):
        self.DEBUG = True
        self.FULLSCREEN = fullscreen
        self.CHANGESCENE = 0
        self.running = False
        # pg.init()
        self.tempres = tempres
        self.res = tempres[0] if self.FULLSCREEN else tempres[1]
        self.mid_screen = (self.res[0] // 2, self.res[1] // 2)
        with open('value.json', 'r') as f:
            self.data = json.load(f)

        pg.display.set_icon(pg.image.load("Image/iconcasino.png"))
        self.screen = pg.display.set_mode(self.res, pg.FULLSCREEN) if self.FULLSCREEN else pg.display.set_mode(self.res, pg.RESIZABLE)
        pg.display.set_caption('Launcher')
        self.clock = pg.time.Clock()
        self.balance = self.data["balance"]

        "Définition des instances"
        self.mid_font = pg.font.Font("Font/Poppins2.ttf", 30)

        self.crashbutton = GameButton("Image/crashbutton1.png", "Image/crashbutton2.png", 1)
        self.gui = GUI()

        if not gen.FULLSCREEN:
            dark_bar()

    def update(self):
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.FULLSCREEN = not self.FULLSCREEN
                    self.res = self.tempres[0] if self.FULLSCREEN else self.tempres[1]
                    self.screen = pg.display.set_mode(self.res, pg.FULLSCREEN) if self.FULLSCREEN else pg.display.set_mode(self.res, pg.RESIZABLE)
                    if not self.FULLSCREEN:
                        pg.display.set_mode(size=self.res,flags=pg.RESIZABLE)
                    self.mid_screen = (self.res[0] // 2, self.res[1] // 2)
                    self.gui.resize()
            elif event.type == pg.VIDEORESIZE:
                self.res = (event.w, event.h)
                if not self.FULLSCREEN:
                    self.tempres[1] = self.res
                self.mid_screen = (self.res[0] // 2, self.res[1] // 2)
                self.gui.resize()
            elif event.type == pg.QUIT:
                pg.quit()
                exit()

        self.pos = pg.mouse.get_pos()
        self.mou = pg.mouse.get_pressed()

        self.screen.fill((35, 35, 35))
        self.crashbutton.update()
        self.gui.update()
        pg.display.update()
        self.clock.tick(30)

def dark_bar():
    """Fonction pour passer la fenêtre en thème sombre"""
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
    hwnd = pg.display.get_wm_info()["window"]
    rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
    value = 2
    value = ct.c_int(value)
    set_window_attribute(hwnd, rendering_policy, ct.byref(value),ct.sizeof(value))
    pg.display.set_mode((gen.res[0]-1,gen.res[1]))
    pg.display.set_mode(gen.res, pg.RESIZABLE)


class GameButton():
    def __init__(self,image1,image2, id):
        self.image_passive = pg.image.load(image1).convert_alpha()
        self.image_active = pg.image.load(image2).convert_alpha()
        self.image = self.image_passive
        self.rect = self.image.get_rect(topleft=(50,50))
        self.base_height = self.rect.bottom
        self.anim_index = 0
        self.id = id

    def update(self):
        if self.rect.collidepoint(gen.pos):
            self.image = self.image_active
            if gen.mou[0]:
                self.click()
            if self.anim_index < 4:
                self.anim_index += 1
        else:
            if self.anim_index != 0:
                self.image = self.image_passive
                self.anim_index -= 1
        self.rect.bottom = self.base_height - self.anim_index
        gen.screen.blit(self.image,self.rect)

    def click(self):
        if self.id == 1:
            gen.CHANGESCENE = 2


class GUI():
    def __init__(self):
        self.resize()

    def resize(self):
        self.text_balance = gen.mid_font.render("¥" + str(gen.balance), True, 'white')
        self.rect_balance = self.text_balance.get_rect(topright=(gen.res[0] - 50, 5))
        self.back_rect = self.rect_balance.copy()
        self.back_rect.width += 20
        self.back_rect.height += 10
        self.back_rect.center = self.rect_balance.center

    def update(self):
        pg.draw.rect(gen.screen, (20,20,20), self.back_rect, border_radius=11)
        gen.screen.blit(self.text_balance, self.rect_balance)






def init(tempres, fullscreen):
    global gen
    gen = Gen()
    gen.crea(tempres, fullscreen)

