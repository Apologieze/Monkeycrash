import pygame as pg
from random import randint
import json

class Gen():
    """A class that generate the crash game"""
    def crea(self, tempres, fullscreen):
        self.DEBUG = False
        self.FULLSCREEN = fullscreen
        self.CHANGESCENE = 0
        self.running = False
        self.tempres = tempres
        self.res = tempres[0] if self.FULLSCREEN else tempres[1]
        self.mid_screen = (self.res[0] // 2, self.res[1] // 2)
        with open('value.json', 'r') as f:
            self.data = json.load(f)

        pg.mixer.init(channels=1)
        pg.mixer.music.load("Music/winning.mp3")
        pg.display.set_icon(pg.image.load("Image/Crash/icon.png"))
        self.screen = pg.display.set_mode(self.res, pg.FULLSCREEN) if self.FULLSCREEN else pg.display.set_mode(self.res,
                                                                                                               pg.RESIZABLE)
        pg.display.set_caption('MonkeyCrash')
        self.clock = pg.time.Clock()
        self.bet_balance = 0.0
        self.initial_bet = 0.0
        self.live_bet = 0.0

        """Création de toutes les instances"""
        self.number_font = pg.font.Font("Font/Poppins2.ttf", 90)
        self.big_font = pg.font.Font("Font/Poppins2.ttf", 40)
        self.mid_font = pg.font.Font("Font/Poppins2.ttf", 30)
        self.small_font = pg.font.Font("Font/Poppins2.ttf", 20)

        self.game_state = Game_state(float(self.data["balance"]))
        self.rocket = pg.sprite.GroupSingle()
        self.rocket.add(Rocket(self.game_state))

        self.courbe = Courbe()
        self.gui = Gui(self.game_state)
        self.history = History()

        self.timer = Timer()


    def update(self):
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_F11:
                    hauteur = self.res[1] - self.rocket.sprite.rect.bottom
                    self.FULLSCREEN = not self.FULLSCREEN
                    self.res = self.tempres[0] if self.FULLSCREEN else self.tempres[1]
                    self.screen = pg.display.set_mode(self.res, pg.FULLSCREEN) if self.FULLSCREEN else pg.display.set_mode(self.res, pg.RESIZABLE)
                    self.rocket.sprite.rect.bottom = self.res[1] - hauteur
                    if not self.FULLSCREEN:
                        pg.display.set_mode(size=self.res,flags=pg.RESIZABLE)
                    self.mid_screen = (self.res[0] // 2, self.res[1] // 2)
                    self.gui.video_size_reset()
                    self.timer.video_size_reset()
                elif event.key == pg.K_ESCAPE:
                    pg.mixer.music.stop()
                    self.CHANGESCENE = 1
                    return
            elif event.type == pg.VIDEORESIZE:
                hauteur = self.res[1] - self.rocket.sprite.rect.bottom
                self.res = (event.w, event.h)
                if not self.FULLSCREEN:
                    self.tempres[1] = self.res
                self.mid_screen = (self.res[0] // 2, self.res[1] // 2)
                self.gui.video_size_reset()
                self.timer.video_size_reset()
                self.rocket.sprite.rect.bottom = self.res[1] - hauteur
            elif event.type == pg.QUIT:
                pg.mixer.music.stop()
                self.CHANGESCENE = 1
                return

        self.mou = pg.mouse.get_pressed()

        self.pos = pg.mouse.get_pos()
        self.screen.fill((21, 25, 55))

        self.courbe.update()

        self.gui.update()

        self.history.update()

        self.rocket.draw(self.screen)
        self.rocket.update()

        self.timer.update()

        pg.display.update()
        self.clock.tick(30)


class Game_state():
    def __init__(self,balance=0.0):
        self.balance = balance

    def generate_multiplicateur(self):
        choice = randint(0, 99)
        if gen.DEBUG:
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
        rocket1 = pg.image.load('Image/Crash/mrocket1.png').convert_alpha()
        rocket2 = pg.image.load('Image/Crash/mrocket2.png').convert_alpha()
        rocket3 = pg.image.load('Image/Crash/mrocket3.png').convert_alpha()

        self.rocket_anim = [rocket1,rocket2,rocket3]
        self.rocket_index = 1
        self.explosion = pg.mixer.Sound("Music/explosion.wav")
        self.move_x = 3
        self.move_y = -1
        self.left = False
        self.fall = False
        self.fall_index = 0

        self.image = self.rocket_anim[1]
        self.rect = self.image.get_rect(bottomleft=(-20, gen.res[1]-150))

        self.multi_max = self.get_multiplicateur()
        self.live_multi = 1.0
        self.multi_color = "white"
        self.multi_add = 0.003
        self.text_multi = gen.big_font.render(str(self.live_multi)+'x', True, 'white')
        self.text_multi_rect = self.text_multi.get_rect(midleft=(self.rect.midright))

    def get_multiplicateur(self):
        r = self.game.generate_multiplicateur()
        if gen.DEBUG:
            print(r)
        return r

    def monter(self):
        if self.move_x > 0:
            if self.rect.right-20 > gen.res[0]:
                self.move_x = 0
        if self.move_y != 0:
            if self.rect.top < 0:
                self.move_y = 0

    def descendre(self):
        if self.fall_index < 50:
            if self.fall_index == 0:
                new_round()
                gen.history.add_value(self.multi_max,self.multi_color)
                self.multi_color = "#ff0000"
                self.explosion.play()
            self.fall_index += 1
        elif self.rect.bottom+110 < gen.res[1]:
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
        self.text_multi = gen.big_font.render(str(self.live_multi)[0:4]+'x', True, self.multi_color)
        if self.left:
            self.text_multi_rect = self.text_multi.get_rect(midright=(self.rect.left, self.rect.centery))
            if self.live_multi > 9:
                self.multi_add = 0.05
        else:
            self.text_multi_rect = self.text_multi.get_rect(midleft=(self.rect.right-30,self.rect.centery))
            if self.text_multi_rect.right+20 >= gen.res[0]:
                self.left = True
                self.multi_add = 0.01
                self.change_animation(1)
        gen.screen.blit(self.text_multi, self.text_multi_rect)

    def update_live_bet(self):
        if not gen.gui.cashout:
            arrondi = 1 if gen.live_bet > 99 else 2
            gen.live_bet = round(gen.initial_bet * self.live_multi,arrondi)

    def reset(self):
        self.rect = self.image.get_rect(bottomleft=(-20, gen.res[1] - 150))
        self.live_multi = 1.0
        self.multi_color = "white"
        self.multi_add = 0.003
        self.move_x = 3
        self.move_y = -1
        self.left = False
        self.change_animation(1)
        gen.running = False
        self.multi_max = self.get_multiplicateur()

    def update(self):
        if gen.running:
            if not self.left and not self.fall:
                if self.rocket_index == 1:
                    self.change_animation(0)
            self.apply_position()
            self.multi_update()
            self.update_live_bet()
        #self.animation_state()

class Courbe():
    def __init__(self):
        self.rect = pg.Rect(0,0,gen.res[0]-10,gen.res[1]-10)
        self.color = "#c9204d"
        self.angle = -0.1
        self.rect.bottomleft = 0, gen.res[1]

    def update(self):
        self.rect.height = gen.res[1]*2-gen.rocket.sprite.rect.center[1]*2.2-150
        self.rect.width = gen.rocket.sprite.rect.center[0]*2
        self.rect.midbottom = (0, gen.res[1]-150)
        pg.draw.arc(gen.screen, self.color, self.rect, 4.71, self.angle, 5)

class Gui():
    def __init__(self,game):
        self.game = game
        self.cashout = False
        self.screen_rect = pg.Rect(gen.res[0]-555, gen.res[1]-70, 330,60)
        self.text_screen = gen.big_font.render(str(gen.bet_balance)+'¥', True, 'white')
        self.static_text = gen.big_font.render("Balance:", True, '#fab3fe')
        self.balance_text = gen.big_font.render(str(self.game.balance) + '¥', True, '#fab3fe')

        self.video_size_reset()

    def video_size_reset(self):
        self.point_y = gen.res[1] - 148
        self.background_rect = pg.Rect(0, self.point_y, gen.res[0], 150)
        self.screen_rect = pg.Rect(gen.res[0] - 555, gen.res[1] - 70, 330, 60)
        self.text_screen_rect = self.text_screen.get_rect(center=self.screen_rect.center)
        self.static_text_rect = self.static_text.get_rect(bottomleft=(10, gen.res[1] - 70))
        self.balance_text_rect = self.balance_text.get_rect(bottomleft=(20, gen.res[1] - 20))

        self.bet_button = Button(gen.res[0] - 200, gen.res[1] - 110, 168, 66, 1, "Placer", gen.big_font, -1, self)
        self.back_bet_button = Button(gen.res[0] - 820, gen.res[1] - 120, 168, 66, 2, "Retirer", gen.big_font, -3, self)
        self.hundred_button = Button(gen.res[0] - 280, gen.res[1] - 110, 60, 30, 0, '+100', gen.small_font, 0, self)
        self.ten_button = Button(gen.res[0] - 350, gen.res[1] - 110, 60, 30, 0, '+10', gen.small_font, 1, self)
        self.one_button = Button(gen.res[0] - 420, gen.res[1] - 110, 60, 30, 0, '+1', gen.small_font, 2, self)
        self.cents_button = Button(gen.res[0] - 490, gen.res[1] - 110, 60, 30, 0, '+0.1', gen.small_font, 3, self)
        self.x_button = Button(gen.res[0] - 560, gen.res[1] - 110, 60, 30, 3, 'X', gen.small_font, -2, self)
        self.reset_live_bet()

    def reset_text(self):
        self.text_screen = gen.big_font.render(str(gen.bet_balance)+'¥', True, 'white')
        self.text_screen_rect = self.text_screen.get_rect(center = self.screen_rect.center)

    def reset_balance_text(self):
        aff_balance = str(int(self.game.balance))+str(self.game.balance%1)[1:4]
        self.balance_text = gen.big_font.render(aff_balance + '¥', True, '#fab3fe')
        self.balance_text_rect = self.balance_text.get_rect(bottomleft=(20, gen.res[1] - 20))

    def reset_live_bet(self):
        self.text_live_bet = gen.mid_font.render("Mise en cours: "+str(gen.live_bet)+'¥', True, 'white')
        self.text_live_bet_rect = self.text_live_bet.get_rect(midright=(self.screen_rect.left - 10, self.screen_rect.centery + 15))

    def update(self):
        pg.draw.rect(gen.screen, "#262626", self.background_rect)
        pg.draw.rect(gen.screen, (20,20,20), self.screen_rect, border_radius=6)
        pg.draw.line(gen.screen, "#853370", (0, self.point_y), (gen.res[0], self.point_y), 7)
        if not gen.running:
            self.bet_button.update()
            self.hundred_button.update()
            self.ten_button.update()
            self.one_button.update()
            self.cents_button.update()
            self.x_button.update()
            self.cashout = False
        else:
            self.reset_live_bet()
            if gen.live_bet != 0:
                self.back_bet_button.update()

        if gen.live_bet >0:
            gen.screen.blit(self.text_live_bet, self.text_live_bet_rect)

        gen.screen.blit(self.text_screen, self.text_screen_rect)
        gen.screen.blit(self.static_text, self.static_text_rect)
        gen.screen.blit(self.balance_text, self.balance_text_rect)

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
        change = [100,10,1,0.1]
        if self.n_id >= 0:
            if gen.bet_balance + change[self.n_id] > gen.game_state.balance:
                temp = str(gen.game_state.balance).split('.')
                gen.bet_balance = round(float(temp[0])+float("0."+temp[1][:min(2,len(temp[1]))]),2)
            else:
                gen.bet_balance = round(gen.bet_balance+change[self.n_id],1)
        elif self.n_id == -2:
            gen.bet_balance = 0.0
        elif self.n_id == -1:
            if gen.bet_balance <= gen.game_state.balance:
                gen.initial_bet = gen.bet_balance
                gen.live_bet = gen.bet_balance
            self.receiver.reset_live_bet()
        elif self.n_id == -3:
            self.retirer()

        self.receiver.reset_text()

    def retirer(self):
        change_balance(gen.live_bet)
        gen.gui.reset_balance_text()
        gen.live_bet = 0.0
        gen.gui.cashout = True

    def update(self):
        #color = self.color_active if self.rect.collidepoint(pos) and not mou[0] else self.color_passive
        if self.rect.collidepoint(gen.pos):
            if gen.mou[0]:
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

        pg.draw.rect(gen.screen, color, self.rect, border_radius=11)
        gen.screen.blit(self.text, self.text_rect)

class Timer():
    def __init__(self):
        self.rect = pg.Rect(0,0,200,200)
        self.video_size_reset()
        self.color = "#0e9dd9"
        self.angle = 90
        self.second = 10
        self.text = gen.number_font.render(str(self.second), True, 'white')
        self.text_rect = self.text.get_rect(center=self.rect.center)

    def video_size_reset(self):
        self.rect.center = gen.mid_screen

    def rad(self,degree):
        return degree*0.01745329251

    def text_refresh(self):
        self.second = 10-int((self.angle-90)*10/-360)
        self.text = gen.number_font.render(str(self.second), True, 'white')
        self.text_rect = self.text.get_rect(center=self.rect.center)

    def reset(self):
        change_balance(-gen.initial_bet)
        gen.gui.reset_balance_text()

        self.angle = 90

    def update(self):
        if not gen.running:
            self.angle -= 1.2
            self.text_refresh()
            pg.draw.arc(gen.screen, self.color, self.rect, 1.57, self.rad(self.angle), 8)
            gen.screen.blit(self.text, self.text_rect)
            if self.second == 0:
                gen.running = True
                pg.mixer.music.play()
                self.reset()

class History():
    """Show the last multipliers"""
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
        text = gen.small_font.render(str(round(n,2)), True, color)
        self.rect_list.insert(0,text.get_rect(topleft=(0,0)))
        self.text_list.insert(0,text)
        self.refresh()

    def refresh(self):
        if self.len > 1:
            for i in range(1,self.len):
                self.rect_list[i].topleft = self.rect_list[i-1].bottomleft

    def update(self):
        for i in range(self.len):
            gen.screen.blit(self.text_list[i], self.rect_list[i])


def new_round():
    pg.mixer.music.stop()
    gen.live_bet, gen.initial_bet = 0.0, 0.0
    gen.gui.reset_live_bet()

def change_balance(n):
    """Change the in game balance and the local balance file"""
    temp = str(gen.game_state.balance + n).split('.')
    gen.game_state.balance = round(float(temp[0]) + float(f"0.{temp[1][:min(2, len(temp[1]))]}"), 2)
    if len(temp[1]) > 2:
        if temp[1][2] == '9':
            gen.game_state.balance = round(gen.game_state.balance + 0.01, 2)
    with open('value.json', 'w') as json_file:
        json.dump({"balance":gen.game_state.balance}, json_file)

def rocket_video_reset(h):
    hauteur = gen.res[1]-gen.rocket.sprite.rect.bottom
    gen.rocket.sprite.rect.bottom = gen.res[1]-hauteur


def init(tempres, fullscreen):
    """Function used to start the game"""
    global gen
    gen = Gen()
    gen.crea(tempres, fullscreen)