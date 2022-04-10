import time
import pygame as pg
from sys import exit
from tkinter import Tk
import ctypes as ct
import json
import subprocess

DEBUG = True
FULLSCREEN = False
running = False
screen_width, screen_height = Tk().winfo_screenwidth(), Tk().winfo_screenheight()
res = (screen_width, screen_height) if FULLSCREEN else (1200, 800)
mid_screen = (res[0] // 2, res[1] // 2)
with open('value.json', 'r') as f:
  data = json.load(f)

pg.init()
pg.display.set_icon(pg.image.load("Image/icon.png"))
screen = pg.display.set_mode(res, pg.FULLSCREEN) if FULLSCREEN else pg.display.set_mode(res, pg.RESIZABLE)
pg.display.set_caption('Launcher')
clock = pg.time.Clock()
balance = data["balance"]

def dark_bar():
    """Fonction pour passer la fenêtre en thème sombre"""
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
    hwnd = pg.display.get_wm_info()["window"]
    rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
    value = 2
    value = ct.c_int(value)
    set_window_attribute(hwnd, rendering_policy, ct.byref(value),ct.sizeof(value))
    pg.display.set_mode((1,1))
    pg.display.set_mode(res, pg.RESIZABLE)


if not FULLSCREEN:
    dark_bar()

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
        if self.rect.collidepoint(pos):
            self.image = self.image_active
            if mou[0]:
                self.click()
            if self.anim_index < 4:
                self.anim_index += 1
        else:
            if self.anim_index != 0:
                self.image = self.image_passive
                self.anim_index -= 1
        self.rect.bottom = self.base_height - self.anim_index
        screen.blit(self.image,self.rect)

    def click(self):
        if self.id == 1:
            import crash


class GUI():
    def __init__(self):
        self.resize()

    def resize(self):
        self.text_balance = mid_font.render("¥" + str(balance), True, 'white')
        self.rect_balance = self.text_balance.get_rect(topright=(res[0] - 50, 5))
        self.back_rect = self.rect_balance.copy()
        self.back_rect.width += 20
        self.back_rect.height += 10
        self.back_rect.center = self.rect_balance.center

    def update(self):
        pg.draw.rect(screen, (20,20,20), self.back_rect, border_radius=11)
        screen.blit(self.text_balance, self.rect_balance)


mid_font = pg.font.Font("Font/Poppins2.ttf", 30)

crashbutton = GameButton("Image/crashbutton1.png", "Image/crashbutton2.png", 1)
gui = GUI()

while True:
    for event in pg.event.get():
        if event.type == pg.VIDEORESIZE:
            res = (event.w, event.h)
            mid_screen = (res[0] // 2, res[1] // 2)
            gui.resize()
        if event.type == pg.QUIT:
            pg.quit()
            exit()

    pos = pg.mouse.get_pos()
    mou = pg.mouse.get_pressed()

    screen.fill((35,35,35))
    crashbutton.update()
    gui.update()
    pg.display.update()
    clock.tick(30)