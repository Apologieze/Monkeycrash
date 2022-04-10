import time
import subprocess
import pygame as pg
from sys import exit
from tkinter import Tk
import ctypes as ct
from random import randint
import json

DEBUG = True
FULLSCREEN = False
running = False
screen_width, screen_height = Tk().winfo_screenwidth(), Tk().winfo_screenheight()
res = (screen_width, screen_height) if FULLSCREEN else (1200, 800)
mid_screen = (res[0] // 2, res[1] // 2)
with open('value.json', 'r') as f:
  data = json.load(f)

pg.init()
pg.mixer.init(channels=1)
pg.mixer.music.load("Music/winning.mp3")
pg.display.set_icon(pg.image.load("Image/icon.png"))
screen = pg.display.set_mode(res, pg.FULLSCREEN) if FULLSCREEN else pg.display.set_mode(res, pg.RESIZABLE)
pg.display.set_caption('MonkeyCrash')
clock = pg.time.Clock()
bet_balance = 0.0
initial_bet = 0.0
live_bet = 0.0

def dark_bar():
    """Fonction pour passer la fenêtre en thème sombre"""
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
    hwnd = pg.display.get_wm_info()["window"]
    rendering_policy = DWMWA_USE_IMMERSIVE_DARK_MODE
    value = 2
    value = ct.c_int(value)
    set_window_attribute(hwnd, rendering_policy, ct.byref(value),ct.sizeof(value))
    pg.display.set_mode((res[0]-1,res[1]))
    pg.display.set_mode(res, pg.RESIZABLE)

if not FULLSCREEN:
    dark_bar()

class Game_state():
    def __init__(self,balance=0.0):
        self.balance = balance

    def generate_multiplicateur(self):
        choice = randint(0, 99)
        if DEBUG:
            print("choice", choice)
        if choice < 10:
            return 1 + (randint(0, 5) / 100)
        elif choice < 40:
            return 1 + (randint(1, 30) / 100)
        elif choice < 70:
            return 1 + (randint(15, 100) / 100)
        elif choice < 88:
            return randint(180, 300) / 100
        elif choice < 95:
            return randint(300, 500) / 100
        elif choice < 97:
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
        self.explosion = pg.mixer.Sound("Music/explosion.wav")
        self.move_x = 3
        self.move_y = -1
        self.left = False
        self.fall = False
        self.fall_index = 0

        self.image = self.rocket_anim[1]
        self.rect = self.image.get_rect(bottomleft=(-20,res[1]-150))

        self.multi_max = self.get_multiplicateur()
        self.live_multi = 1.0
        self.multi_color = "white"
        self.multi_add = 0.003
        self.text_multi = big_font.render(str(self.live_multi)+'x', True, 'white')
        self.text_multi_rect = self.text_multi.get_rect(midleft=(self.rect.midright))

    def get_multiplicateur(self):
        r = self.game.generate_multiplicateur()
        if DEBUG:
            print(r)
        return r

    def monter(self):
        if self.move_x > 0:
            if self.rect.right-20 > res[0]:
                self.move_x = 0
        if self.move_y != 0:
            if self.rect.top < 0:
                self.move_y = 0

    def descendre(self):
        if self.fall_index < 50:
            if self.fall_index == 0:
                new_round()
                historic.add_value(self.multi_max,self.multi_color)
                self.multi_color = "#ff0000"
                self.explosion.play()
            self.fall_index += 1
        elif self.rect.bottom+110 < res[1]:
            self.rect.bottom += 10
        else:
            self.fall = False
            self.fall_index = 0
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

    def multi_update(self):  # sourcery skip: assign-if-exp
        if self.live_multi >= self.multi_max:
            self.fall = True
            self.change_animation(2)
        if not self.fall:
            self.live_multi += self.multi_add
            if self.live_multi > 1.8:
                if self.live_multi > 2.8:
                    if self.live_multi > 6:
                        self.multi_color = "#ffd557"
                    else:
                        self.multi_color = "#63ffa9"
                else:
                    self.multi_color = "#7adfff"
        self.text_multi = big_font.render(str(self.live_multi)[0:4]+'x', True, self.multi_color)
        if self.left:
            self.text_multi_rect = self.text_multi.get_rect(midright=(self.rect.left, self.rect.centery))
            if self.live_multi > 9:
                self.multi_add = 0.05
        else:
            self.text_multi_rect = self.text_multi.get_rect(midleft=(self.rect.right-30,self.rect.centery))
            if self.text_multi_rect.right+20 >= res[0]:
                self.left = True
                self.multi_add = 0.01
                self.change_animation(1)
        screen.blit(self.text_multi, self.text_multi_rect)

    def update_live_bet(self):
        global live_bet
        if not gui.cashout:
            arrondi = 1 if live_bet > 99 else 2
            live_bet = round(initial_bet * self.live_multi,arrondi)

    def reset(self):
        global running
        self.rect = self.image.get_rect(bottomleft=(-20, res[1] - 150))
        self.live_multi = 1.0
        self.multi_color = "white"
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
            self.update_live_bet()
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
    def __init__(self,game):
        self.game = game
        self.cashout = False
        self.screen_rect = pg.Rect(res[0]-555, res[1]-70, 330,60)
        self.text_screen = big_font.render(str(bet_balance)+'¥', True, 'white')
        self.static_text = big_font.render("Balance:", True, '#fab3fe')
        self.balance_text = big_font.render(str(self.game.balance) + '¥', True, '#fab3fe')

        self.video_size_reset()

    def video_size_reset(self):
        self.point_y = res[1] - 148
        self.background_rect = pg.Rect(0, self.point_y, res[0], 150)
        self.screen_rect = pg.Rect(res[0] - 555, res[1] - 70, 330, 60)
        self.text_screen_rect = self.text_screen.get_rect(center=self.screen_rect.center)
        self.static_text_rect = self.static_text.get_rect(bottomleft=(10, res[1] - 70))
        self.balance_text_rect = self.balance_text.get_rect(bottomleft=(20, res[1] - 20))

        self.bet_button = Button(res[0] - 200, res[1] - 110, 168, 66, 1, "Placer", big_font, -1, self)
        self.back_bet_button = Button(res[0] - 820, res[1] - 120, 168, 66, 2, "Retirer", big_font, -3, self)
        self.hundred_button = Button(res[0] - 280, res[1] - 110, 60, 30, 0, '+100', small_font, 0, self)
        self.ten_button = Button(res[0] - 350, res[1] - 110, 60, 30, 0, '+10', small_font, 1, self)
        self.one_button = Button(res[0] - 420, res[1] - 110, 60, 30, 0, '+1', small_font, 2, self)
        self.cents_button = Button(res[0] - 490, res[1] - 110, 60, 30, 0, '+0.1', small_font, 3, self)
        self.x_button = Button(res[0] - 560, res[1] - 110, 60, 30, 3, 'X', small_font, -2, self)
        self.reset_live_bet()

    def reset_text(self):
        self.text_screen = big_font.render(str(bet_balance)+'¥', True, 'white')
        self.text_screen_rect = self.text_screen.get_rect(center = self.screen_rect.center)

    def reset_balance_text(self):
        aff_balance = str(int(self.game.balance))+str(self.game.balance%1)[1:4]
        self.balance_text = big_font.render(aff_balance + '¥', True, '#fab3fe')
        self.balance_text_rect = self.balance_text.get_rect(bottomleft=(20, res[1] - 20))

    def reset_live_bet(self):
        self.text_live_bet = mid_font.render("Mise en cours: "+str(live_bet)+'¥', True, 'white')
        self.text_live_bet_rect = self.text_live_bet.get_rect(midleft = (self.screen_rect.left-310, self.screen_rect.centery+15))

    def update(self):
        pg.draw.rect(screen, "#262626", self.background_rect)
        pg.draw.rect(screen, (20,20,20), self.screen_rect, border_radius=6)
        pg.draw.line(screen, "#853370", (0, self.point_y), (res[0], self.point_y), 7)
        if not running:
            self.bet_button.update()
            self.hundred_button.update()
            self.ten_button.update()
            self.one_button.update()
            self.cents_button.update()
            self.x_button.update()
            self.cashout = False
        else:
            self.reset_live_bet()
            if live_bet != 0:
                self.back_bet_button.update()

        if live_bet >0:
            screen.blit(self.text_live_bet, self.text_live_bet_rect)

        screen.blit(self.text_screen, self.text_screen_rect)
        screen.blit(self.static_text, self.static_text_rect)
        screen.blit(self.balance_text, self.balance_text_rect)

class Button():
    def __init__(self,left,top,width,height,color,text,font,n_id,receiver=None):
        self.triggered = False
        self.receiver = receiver
        self.n_id = n_id
        self.rect = pg.Rect(left,top,width,height)
        self.color_passive, self.color_active = ('#6441A4', "#392E5C") if color == 1 else ('#0E9DD9', '#12769e')
        if color == 3:
            self.color_passive, self.color_active = '#D23636', '#881f1e'
        elif color == 2:
            self.color_passive, self.color_active = '#fb7e18', '#c36518'
        self.text = font.render(text, True, 'white')
        self.text_rect = self.text.get_rect(center=self.rect.center)

    def adding(self):
        global bet_balance, live_bet, initial_bet
        change = [100,10,1,0.1]
        if self.n_id >= 0:
            if bet_balance + change[self.n_id] > game_state.balance:
                bet_balance = game_state.balance
            else:
                bet_balance = round(bet_balance+change[self.n_id],1)
        elif self.n_id == -2:
            bet_balance = 0.0
        elif self.n_id == -1:
            if bet_balance <= game_state.balance:
                initial_bet = bet_balance
                live_bet = bet_balance
            self.receiver.reset_live_bet()
        elif self.n_id == -3:
            self.retirer()

        self.receiver.reset_text()

    def retirer(self):
        global live_bet
        change_balance(live_bet)
        gui.reset_balance_text()
        live_bet = 0.0
        gui.cashout = True

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
        self.video_size_reset()
        self.color = "#0e9dd9"
        self.angle = 90
        self.second = 10
        self.text = number_font.render(str(self.second), True, 'white')
        self.text_rect = self.text.get_rect(center=self.rect.center)

    def video_size_reset(self):
        self.rect.center = mid_screen

    def rad(self,degree):
        return degree*0.01745329251

    def text_refresh(self):
        self.second = 10-int((self.angle-90)*10/-360)
        self.text = number_font.render(str(self.second), True, 'white')
        self.text_rect = self.text.get_rect(center=self.rect.center)

    def reset(self):
        change_balance(-initial_bet)
        gui.reset_balance_text()

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
                pg.mixer.music.play()
                self.reset()

class Historic():
    def __init__(self):
        self.text_list = []
        self.rect_list = []
        self.len = 0

    def add_value(self,n,color):
        if self.len == 5:
            self.text_list.pop()
            self.rect_list.pop()
        else:
            self.len += 1
        text = small_font.render(str(round(n,2)), True, color)
        self.rect_list.insert(0,text.get_rect(topleft=(0,0)))
        self.text_list.insert(0,text)
        self.refresh()

    def refresh(self):
        if self.len > 1:
            for i in range(1,self.len):
                self.rect_list[i].topleft = self.rect_list[i-1].bottomleft

    def update(self):
        for i in range(self.len):
            screen.blit(self.text_list[i], self.rect_list[i])


def new_round():
    global live_bet, initial_bet
    pg.mixer.music.stop()
    live_bet, initial_bet = 0.0, 0.0
    gui.reset_live_bet()

def change_balance(n):
    game_state.balance += n
    with open('value.json', 'w') as json_file:
        json.dump({"balance":round(game_state.balance,2)}, json_file)

def rocket_video_reset(h):
    hauteur = res[1]-rocket.sprite.rect.bottom
    rocket.sprite.rect.bottom = res[1]-hauteur

"""Création de toutes les instances"""
number_font = pg.font.Font("Font/Poppins2.ttf", 90)
big_font = pg.font.Font("Font/Poppins2.ttf", 40)
mid_font = pg.font.Font("Font/Poppins2.ttf", 30)
small_font = pg.font.Font("Font/Poppins2.ttf", 20)

game_state = Game_state(data["balance"])
rocket = pg.sprite.GroupSingle()
rocket.add(Rocket(game_state))

courbe = Courbe()
gui = Gui(game_state)
historic = Historic()


timer = Timer()

while True:
    for event in pg.event.get():
        if event.type == pg.VIDEORESIZE:
            hauteur = res[1] - rocket.sprite.rect.bottom
            res = (event.w, event.h)
            mid_screen = (res[0] // 2, res[1] // 2)
            gui.video_size_reset()
            timer.video_size_reset()
            rocket.sprite.rect.bottom = res[1]-hauteur
            # screen = pg.display.set_mode(res, pg.RESIZABLE)
        if event.type == pg.QUIT:
            import launcher
            pg.quit()
            exit()


    mou = pg.mouse.get_pressed()

    pos = pg.mouse.get_pos()
    screen.fill((21,25,55))

    courbe.update()

    gui.update()

    historic.update()

    rocket.draw(screen)
    rocket.update()

    timer.update()

    pg.display.update()
    clock.tick(30)
