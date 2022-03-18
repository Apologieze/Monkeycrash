from random import randint
import pygame as pg
from sys import exit
from tkinter import Tk
import ctypes as ct
from random import randint


DEBUG = False
FULLSCREEN = False
running = False
screen_width, screen_height = Tk().winfo_screenwidth(), Tk().winfo_screenheight()
res = (screen_width, screen_height) if FULLSCREEN else (1200, 800)
mid_screen = (res[0] // 2, res[1] // 2)

pg.init()
screen = pg.display.set_mode(res, pg.FULLSCREEN) if FULLSCREEN else pg.display.set_mode(res)
pg.display.set_caption('Monke Crash')
clock = pg.time.Clock()
bet_balance = 0.0
# pg.mouse.set_visible(False)

"""Fonction pour passer la fenêtre en thème sombre"""
def dark_bar():
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
    hwnd = pg.display.get_wm_info()["window"]
    rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
    value = 2
    value = ct.c_int(value)
    set_window_attribute(hwnd, rendering_policy, ct.byref(value),ct.sizeof(value))
    pg.display.set_mode((1,1))
    pg.display.set_mode(res)

class Game_state():
    def generate_multiplicateur(self):
        choice = randint(0, 99)
        print("choice", choice)
        if choice < 10:
            return 1 + (randint(0, 5) / 100)
        elif choice < 30:
            return 1 + (randint(1, 50) / 100)
        elif choice < 60:
            return 1 + (randint(50, 100) / 100)
        elif choice < 85:
            return randint(200, 300) / 100
        elif choice < 90:
            return randint(300, 500) / 100
        elif choice < 95:
            return randint(500, 999) / 100
        elif choice < 99:
            return randint(1000, 5000) / 100
        else:
            return randint(5000, 10000) / 100


class Rocket(pg.sprite.Sprite):
    def __init__(self,game):
        super().__init__()
        self.game = game
        rocket1 = pg.image.load('Image/mrocket1.png').convert_alpha()
        rocket2 = pg.image.load('Image/mrocket2.png').convert_alpha()
        rocket3 = pg.image.load('Image/mrocket3.png').convert_alpha()

        self.rocket_anim = [rocket1,rocket2,rocket3]
        self.rocket_index = 1
        self.move_x = 3
        self.move_y = -1
        self.left = False
        self.fall = False

        self.image = self.rocket_anim[1]
        self.rect = self.image.get_rect(bottomleft=(-20,res[1]-150))

        self.multi_max = self.get_multiplicateur()
        print(self.multi_max)
        self.live_multi = 1.0
        self.multi_add = 0.003
        self.text_multi = big_font.render(str(self.live_multi)+'x', True, 'white')
        self.text_multi_rect = self.text_multi.get_rect(midleft=(self.rect.midright))

    def get_multiplicateur(self):
        return self.game.generate_multiplicateur()

    def monter(self):
        if self.move_x > 0:
            if self.rect.right-20 > res[0]:
                self.move_x = 0
        if self.move_y != 0:
            if self.rect.top < 0:
                self.move_y = 0

    def descendre(self):
        if self.rect.bottom+130 < res[1]:
            self.rect.bottom += 10
        else:
            self.fall = False
            self.reset()

    def apply_position(self):
        if self.fall:
            self.descendre()
        else:
            self.monter()
            self.rect.bottomleft = self.rect.left + self.move_x, self.rect.bottom + self.move_y

    def change_animation(self,n):
        self.image = self.rocket_anim[n]
        self.rocket_index = n

    def multi_update(self):
        if self.live_multi >= self.multi_max:
            self.fall = True
            self.change_animation(2)
        if not self.fall:
            self.live_multi += self.multi_add
        self.text_multi = big_font.render(str(self.live_multi)[0:4]+'x', True, 'white')
        if self.left:
            self.text_multi_rect = self.text_multi.get_rect(midright=(self.rect.left, self.rect.centery))
        else:
            self.text_multi_rect = self.text_multi.get_rect(midleft=(self.rect.right-30,self.rect.centery))
            if self.text_multi_rect.right+20 >= res[0]:
                self.left = True
                self.multi_add = 0.01
                self.change_animation(1)
        screen.blit(self.text_multi, self.text_multi_rect)

    def reset(self):
        global running
        self.rect = self.image.get_rect(bottomleft=(-20, res[1] - 150))
        self.live_multi = 1.0
        self.multi_add = 0.003
        self.move_x = 3
        self.move_y = -1
        self.left = False
        self.change_animation(1)
        running = False
        self.multi_max = self.get_multiplicateur()

    def update(self):
        if running:
            if not self.left and not self.fall:
                if self.rocket_index == 1:
                    self.change_animation(0)
            self.apply_position()
            self.multi_update()
        #self.animation_state()

class Courbe():
    def __init__(self):
        self.rect = pg.Rect(0,0,res[0]-10,res[1]-10)
        self.color = "#c9204d"
        self.angle = -0.1
        self.rect.bottomleft = 0, res[1]

    def update(self):
        self.rect.height = res[1]*2-rocket.sprite.rect.center[1]*2.2-150
        self.rect.width = rocket.sprite.rect.center[0]*2
        self.rect.midbottom = (0, res[1]-150)
        pg.draw.arc(screen, self.color, self.rect, 4.71, self.angle, 5)

class Gui():
    def __init__(self):
        self.point_y = res[1]-148
        self.background_rect = pg.Rect(0, self.point_y, res[0], 150)
        self.screen_rect = pg.Rect(res[0]-555, res[1]-70, 330,60)
        self.text_screen = big_font.render(str(bet_balance)+'¥', True, 'white')
        self.text_screen_rect = self.text_screen.get_rect(center = self.screen_rect.center)

        self.bet_button = Button(res[0] - 200, res[1] - 110, 168, 66, 1, "Placer", big_font,-1,self)

        self.hundred_button = Button(res[0] - 280, res[1] - 110, 60, 30, 0, '+100', small_font,0,self)
        self.ten_button = Button(res[0] - 350, res[1] - 110, 60, 30, 0, '+10', small_font,1,self)
        self.one_button = Button(res[0] - 420, res[1] - 110, 60, 30, 0, '+1', small_font,2,self)
        self.cents_button = Button(res[0] - 490, res[1] - 110, 60, 30, 0, '+0.1', small_font,3,self)
        self.x_button = Button(res[0] - 560, res[1] - 110, 60, 30, 3, 'X', small_font,-2,self)

    def reset_text(self):
        self.text_screen = big_font.render(str(bet_balance)+'¥', True, 'white')
        self.text_screen_rect = self.text_screen.get_rect(center = self.screen_rect.center)

    def update(self):
        pg.draw.rect(screen, "#262626", self.background_rect)
        pg.draw.rect(screen, (20,20,20), self.screen_rect, border_radius=6)
        pg.draw.line(screen, "#853370", (0, self.point_y), (res[0], self.point_y), 7)
        self.bet_button.update()
        self.hundred_button.update()
        self.ten_button.update()
        self.one_button.update()
        self.cents_button.update()
        self.x_button.update()
        screen.blit(self.text_screen, self.text_screen_rect)

class Button():
    def __init__(self,left,top,width,height,color,text,font,n_id,receiver=None):
        self.triggered = False
        self.receiver = receiver
        self.n_id = n_id
        self.rect = pg.Rect(left,top,width,height)
        self.color_passive, self.color_active = ('#6441A4', "#392E5C") if color == 1 else ('#0E9DD9', '#12769e')
        if color == 3:
            self.color_passive, self.color_active = '#D23636', '#881f1e'
        self.text = font.render(text, True, 'white')
        self.text_rect = self.text.get_rect(center=self.rect.center)

    def adding(self):
        global bet_balance
        change = [100,10,1,0.1]
        if self.n_id >= 0:
            bet_balance = round(bet_balance+change[self.n_id],1)
        elif self.n_id == -2:
            bet_balance = 0.0
        self.receiver.reset_text()


    def update(self):
        #color = self.color_active if self.rect.collidepoint(pos) and not mou[0] else self.color_passive
        if self.rect.collidepoint(pos):
            if mou[0]:
                color = self.color_passive
                if not self.triggered:
                    self.adding()
                    self.triggered = True
            else:
                color = self.color_active
                if self.triggered:
                    self.triggered = False
        else:
            color = self.color_passive
            if self.triggered:
                self.triggered = False

        pg.draw.rect(screen, color, self.rect, border_radius=11)
        screen.blit(self.text, self.text_rect)

class Timer():
    def __init__(self):
        self.rect = pg.Rect(0,0,200,200)
        self.rect.center = mid_screen
        self.color = "#0e9dd9"
        self.angle = 90
        self.second = 10
        self.text = number_font.render(str(self.second), True, 'white')
        self.text_rect = self.text.get_rect(center=self.rect.center)

    def rad(self,degree):
        return degree*0.01745329251

    def text_refresh(self):
        self.second = 10-int((self.angle-90)*10/-360)
        self.text = number_font.render(str(self.second), True, 'white')
        self.text_rect = self.text.get_rect(center=self.rect.center)

    def reset(self):
        self.angle = 90

    def update(self):
        global running
        if not running:
            self.angle -= 1.2
            self.text_refresh()
            pg.draw.arc(screen, self.color, self.rect, 1.57, self.rad(self.angle), 8)
            screen.blit(self.text, self.text_rect)
            if self.second == 0:
                running = True
                self.reset()



if not FULLSCREEN:
    dark_bar()

"""Création de toutes les instances"""
number_font = pg.font.Font("Image\Poppins2.ttf", 90)
big_font = pg.font.Font("Image\Poppins2.ttf", 40)
small_font = pg.font.Font("Image\Poppins2.ttf", 20)

rocket = pg.sprite.GroupSingle()
rocket.add(Rocket(Game_state()))

courbe = Courbe()

gui = Gui()

timer = Timer()

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()

    mou = pg.mouse.get_pressed()

    pos = pg.mouse.get_pos()
    screen.fill("#151937")

    courbe.update()

    gui.update()

    rocket.draw(screen)
    rocket.update()

    timer.update()

    pg.display.update()
    clock.tick(30)