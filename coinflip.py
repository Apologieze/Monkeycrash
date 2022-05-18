import pygame as pg
import json

class Gen:
    def crea(self, tempres, fullscreen):
        self.DEBUG = True
        self.FULLSCREEN = fullscreen
        self.CHANGESCENE = 0
        self.running = False
        self.tempres = tempres
        self.res = tempres[0] if self.FULLSCREEN else tempres[1]
        self.mid_screen = (self.res[0] // 2, self.res[1] // 2)
        with open('value.json', 'r') as f:
            self.data = json.load(f)

        pg.display.set_icon(pg.image.load("Image/Monkeycoin/icon.png"))
        self.screen = pg.display.set_mode(self.res, pg.FULLSCREEN) if self.FULLSCREEN else pg.display.set_mode(self.res, pg.RESIZABLE)
        pg.display.set_caption('MonkeyCoin')
        self.clock = pg.time.Clock()
        self.balance = float(self.data["balance"])
        self.bet_balance = 0.0
        self.live_bet = 0.0

        "Définition des instances"
        self.number_font = pg.font.Font("Font/Poppins2.ttf", 90)
        self.big_font = pg.font.Font("Font/Poppins2.ttf", 40)
        self.mid_font = pg.font.Font("Font/Poppins2.ttf", 30)
        self.small_font = pg.font.Font("Font/Poppins2.ttf", 20)

        self.coin = Coin()
        self.gui = GUI()

    def update(self):
        # sourcery skip: merge-duplicate-blocks, remove-pass-elif, remove-redundant-if
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_F11:
                    self.FULLSCREEN = not self.FULLSCREEN
                    self.res = self.tempres[0] if self.FULLSCREEN else self.tempres[1]
                    self.screen = pg.display.set_mode(self.res, pg.FULLSCREEN) if self.FULLSCREEN else pg.display.set_mode(self.res, pg.RESIZABLE)
                    if not self.FULLSCREEN:
                        pg.display.set_mode(size=self.res,flags=pg.RESIZABLE)
                    self.mid_screen = (self.res[0] // 2, self.res[1] // 2)
                    self.gui.resize()
                elif event.key == pg.K_ESCAPE:
                    self.CHANGESCENE = 1
                    return
            elif event.type == pg.VIDEORESIZE:
                self.res = (event.w, event.h)
                if not self.FULLSCREEN:
                    self.tempres[1] = self.res
                self.mid_screen = (self.res[0] // 2, self.res[1] // 2)
                self.gui.resize()
            elif event.type == pg.QUIT:
                self.CHANGESCENE = 1
                return

        self.pos = pg.mouse.get_pos()
        self.mou = pg.mouse.get_pressed()

        self.screen.fill((35, 35, 35))
        self.coin.update()
        self.gui.update()
        pg.display.update()
        self.clock.tick(30)


class DisplayBalance():
    def __init__(self):
        self.resize()

    def resize(self):
        self.text_balance = gen.mid_font.render("¥" + str(gen.balance), True, 'white')
        self.rect_balance = self.text_balance.get_rect(topright=(gen.res[0] - 20, 10))
        self.back_rect = self.rect_balance.copy()
        self.back_rect.width += 20
        self.back_rect.height += 10
        self.back_rect.center = self.rect_balance.center

    def update(self):
        pg.draw.rect(gen.screen, (20,20,20), self.back_rect, border_radius=11)
        gen.screen.blit(self.text_balance, self.rect_balance)

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
            if gen.bet_balance + change[self.n_id] > gen.balance:
                temp = str(gen.balance).split('.')
                gen.bet_balance = float(temp[0])+float("0."+temp[1][:min(2,len(temp[1]))])
            else:
                gen.bet_balance = round(gen.bet_balance+change[self.n_id],1)
        elif self.n_id == -2:
            gen.bet_balance = 0.0
        elif self.n_id == -1:
            if gen.bet_balance <= gen.balance:
                gen.live_bet = gen.bet_balance
            self.receiver.reset_live_bet()

        self.receiver.reset_text()

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

class Coin():
    def __init__(self):
        self.anim_coin = []
        self.frame = 0
        self.speed = 0.07
        for i in range(60):
            self.anim_coin.append(pg.image.load(f'Image/Monkeycoin/Frame/frame_{i}_delay-0.03s.png').convert_alpha())
        self.image = self.anim_coin[self.frame]
        self.rect = self.image.get_rect()
        self.resize()

    def resize(self):
        self.rect.center = (gen.mid_screen[0], gen.mid_screen[1] - gen.mid_screen[1] // 4)

    def update(self):
        gen.screen.blit(self.image, self.rect)

class GUI():
    def __init__(self):
        self.display_balance = DisplayBalance()
        self.screen_rect = pg.Rect(gen.res[0] - 555, gen.res[1] - 70, 330, 60)
        self.text_screen = gen.big_font.render(str(gen.bet_balance) + '¥', True, 'white')

        self.video_size_reset()

    def video_size_reset(self):
        self.point_y = gen.res[1] - 148
        self.background_rect = pg.Rect(0, self.point_y, gen.res[0], 150)
        self.screen_rect = pg.Rect(gen.res[0] - 555, gen.res[1] - 70, 330, 60)
        self.text_screen_rect = self.text_screen.get_rect(center=self.screen_rect.center)

        self.bet_button = Button(gen.res[0] - 200, gen.res[1] - 110, 168, 66, 1, "Placer", gen.big_font, -1, self)
        self.hundred_button = Button(gen.res[0] - 280, gen.res[1] - 110, 60, 30, 0, '+100', gen.small_font, 0, self)
        self.ten_button = Button(gen.res[0] - 350, gen.res[1] - 110, 60, 30, 0, '+10', gen.small_font, 1, self)
        self.one_button = Button(gen.res[0] - 420, gen.res[1] - 110, 60, 30, 0, '+1', gen.small_font, 2, self)
        self.cents_button = Button(gen.res[0] - 490, gen.res[1] - 110, 60, 30, 0, '+0.1', gen.small_font, 3, self)
        self.x_button = Button(gen.res[0] - 560, gen.res[1] - 110, 60, 30, 3, 'X', gen.small_font, -2, self)
        self.reset_live_bet()

    def reset_text(self):
        self.text_screen = gen.big_font.render(str(gen.bet_balance) + '¥', True, 'white')
        self.text_screen_rect = self.text_screen.get_rect(center=self.screen_rect.center)

    def reset_live_bet(self):
        self.text_live_bet = gen.mid_font.render("Mise en cours: " + str(gen.live_bet) + '¥', True, 'white')
        self.text_live_bet_rect = self.text_live_bet.get_rect(midright=(self.screen_rect.left - 10, self.screen_rect.centery + 15))

    def resize(self):
        gen.coin.resize()
        self.display_balance.resize()
        self.video_size_reset()

    def update(self):
        self.display_balance.update()
        pg.draw.rect(gen.screen, "#262626", self.background_rect)
        pg.draw.rect(gen.screen, (20, 20, 20), self.screen_rect, border_radius=6)
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

        if gen.live_bet > 0:
            gen.screen.blit(self.text_live_bet, self.text_live_bet_rect)

        gen.screen.blit(self.text_screen, self.text_screen_rect)


def init(tempres, fullscreen):
    global gen
    gen = Gen()
    gen.crea(tempres, fullscreen)

