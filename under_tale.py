import math
import random
import time
import sys
from typing import Any
import pygame as pg
import os

from pygame.sprite import AbstractGroup


WIDTH = 800
HEIGHT = 500
STAGE_TOP = 200
STAGE_BOTTOM = 400
STAGE_LEFT = 205
STAGE_RIGHT = 590

main_dir = os.path.split(os.path.abspath(__file__))[0]


def load_sound(file):
    """"""
    if not pg.mixer:
        return None
    file = os.path.join(main_dir, "data", file)
    try:
        sound = pg.mixer.Sound(file)
        return sound
    except pg.error:
        print("Warning, unable to load, %s" % file)
    return None


class Enemy(pg.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.img =  pg.transform.scale(pg.image.load("ex05\data\pngwingcom_negate.png"), (250, 150))

    def update(self, screen: pg.Surface):
        self.img.set_colorkey((0, 0, 0))
        screen.blit(self.img, (275, 25))

# プレイヤーが画面内にいるかどうかの判定処理
def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    yoko, tate = True, True
    if obj_rct.left < 390/2+10 or 595 < obj_rct.right:
        yoko = False
    if obj_rct.top < 205 or 395 < obj_rct.bottom:
        tate = False
    return yoko, tate

# 説明分を作成・表示
class Explanation(pg.sprite.Sprite):
    """説明文の表示をするExplanationクラス"""
    def __init__(self, str_):
        self.str = str_
        self.font = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
        self.color = (255, 255, 255)
        self.img = self.font.render(f"{self.str}", True, self.color)
        self.rct = self.img.get_rect()
        # self.rct.center = WIDTH/2, HEIGHT/2
    
    def update(self, sur:pg.Surface, lst=[0,0]):
        self.img = self.font.render(f"{self.str}", True, self.color)
        sur.blit(self.img, lst)



class Command(pg.sprite.Sprite):
    """ コマンドのインターフェースを表示をするCommandクラス"""
    def __init__(self, name, x, y):
        """ 引数にname：コマンドの名前
            x,y：表示する座標"""
        self.name = name
        self.font = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
        self.color = (255, 255, 255)
        self.img = self.font.render(f"{self.name}", True, self.color)
        self.rct = self.img.get_rect()
        self.rct.center = x, y

    def update(self, screen:pg.Surface):
        """ 画面表示の更新
            引数 screen : 表示するscreen"""
        self.img = self.font.render(f"{self.name}", True, self.color)
        screen.blit(self.img, self.rct)

    def color_update(self, color:tuple):
        """文字色の更新をする
            引数 color : 色の情報を入れたタプル
        """
        self.color = color


# プレイヤーの動きの制御
class player_move:
    
    delta = { # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, 1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    def __init__(self, xy: tuple[float, float]):
        self.image = pg.transform.flip(  # 左右反転
            pg.transform.rotozoom( 
                pg.image.load(f"ex05/fig/0.png"), 0, 0.02), True, False)
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.on_the_ground = False
        self.jump = False
        self.jump_tmr = 0

    # プレイヤーの表示位置の更新処理
    def update(self,key_lst: list[bool],screen:pg.Surface, gravity=None, hop=None):
        self.sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                self.sum_mv[0] += mv[0]
                self.sum_mv[1] += mv[1]
        if gravity and not self.jump:
            self.sum_mv[1] = 1
        elif hop:
            self.sum_mv[1] = hop
        self.rect.move_ip(self.sum_mv)
        if self.rect[1]<205:#上
            self.rect[1]=205
        if self.rect[1]>376:#した
            self.rect[1]=376
            self.on_the_ground = True
            self.jump = False
            self.jump_tmr = 0
        if self.rect[0]>578:#右
            self.rect[0]=578
        if self.rect[0]<205:#左
            self.rect[0]=205

        screen.blit(self.image, self.rect)



# HP関連の機能を実装するためのクラス
class Hp:
    def __init__(self):
        self.width = 100

    #文字を生成するためのインスタンス
    def genfont(self, txt): 
        self.fonto = pg.font.Font(None, 25)
        self.txt = self.fonto.render(txt, True, (255, 255, 255))

    #　図形を生成するためのインスタンス
    def genobj(self, color, locate, sur: pg.Surface):
        self.color = color
        self.locate = locate
        self.rct = pg.draw.rect(sur, color, locate)

    # 文字と図形で違う処理で更新するインスタンス
    def update(self, sur: pg.Surface, xy=None, txt=None, color=(255, 255, 255)):
        if txt: # 文字を生成
            self.obj = self.fonto.render(txt, True, color)
            sur.blit(self.obj, xy)
        elif self.rct: #　図形を生成
            pg.draw.rect(sur, self.color, self.locate)


# プレイヤーがfightコマンドを選択した場合の処理        
def attack_action(attack_bar_lis, sur: pg.Surface):
    attack_sur = pg.Surface((600, 200))
    pg.draw.rect(attack_sur, (255, 255, 255), (0, 0, 600, 200))
    pg.draw.rect(attack_sur, (0, 0, 0), (5, 5, 590, 190))
    img = pg.transform.rotozoom(pg.image.load(f"ex05/undertale_attack.png"), 0, 0.49)
    attack_sur.blit(img, (6, 50))
    # バーが画面端に到達したら進行方向を逆にする
    if attack_bar_lis[0] < 10 or 580 < attack_bar_lis[0]:
        attack_bar_lis[1] *= -1
    attack_bar_lis[0] += attack_bar_lis[1] # バーの位置をattack_bar_lis[1]分ずらす
    pg.draw.rect(attack_sur, (255, 255, 255), (attack_bar_lis[0], 25, 10, 150))
    sur.blit(attack_sur, (0, 0))
    


# 以下敵の攻撃についての機能の実装
def calc_orientation(org: pg.Rect, pre_x, pre_y):
    """
    orgから見て, pos_x, pos_yがどこにあるかを計算し, 方向ベクトルをタプルで返す
    引数1 org: 爆弾SurfaceのRect
    引数2 pos_x: 目標のx座標
    引数3 pos_y: 目標のy座標
    戻り値: orgから見た目標の方向ベクトルを表すタプル
    """
    x_diff, y_diff = pre_x-org.centerx, pre_y-org.centery
    norm = math.sqrt(x_diff**2+y_diff**2)
    return x_diff/norm, y_diff/norm


def check_out(obj: pg.Rect):
    """
    弾が画面外に出たかを判定する関数
    引数 obj: 弾のRect
    横方向 縦方向のはみ出し判定結果
    （画面内: True/画面外: False）
    """
    yoko, tate = True, True
    if obj.right < -5 or WIDTH+5 < obj.left:
        yoko = False
    if obj.bottom < -5 or HEIGHT+5 < obj.bottom:
        tate = False
    return yoko, tate


def gen_flower(pre_x, pre_y):
    """
    拡散弾幕を生成する関数
    引数1 pre_x: 中心x座標
    引数2 pre_x: 中心y座標
    変数1 pos_x: 発射するx座標
    変数2 pos_y: 発射するy座標
    戻り値 flos: リスト
    """
    num = 8
    flos = []
    for theta in range(0, 360, int(360/num)):
        if theta == 0:
            pos_x = pre_x + 5
            pos_y = pre_y
        elif 0 < theta < 90:
            pos_x = pre_x + 5
            pos_y = pre_y - 5
        elif theta == 90:
            pos_x = pre_x
            pos_y = pre_y - 5
        elif 90 < theta < 180:
            pos_x = pre_x - 5
            pos_y = pre_y - 5
        elif theta == 180:
            pos_x = pre_x - 5
            pos_y = pre_y
        elif 180 < theta < 270:
            pos_x = pre_x - 5
            pos_y = pre_y + 5
        elif theta == 270:
            pos_x = pre_x
            pos_y = pre_y + 5
        elif 270 < theta < 360:
            pos_x = pre_x + 5
            pos_y = pre_y + 5

        flos.append(Bullet(pre_x, pre_y, pos_x, pos_y))
    return flos


def calc_degree(pos_x, pos_y, pl_x, pl_y):
    """
    プレイヤー座標と発射座標の角度を求める関数
    引数1 pos_x: 発射x座標
    引数2 pos_y: 発射y座標
    引数3 pl_x: プレイヤーx座標
    引数4 pl_y: プレイヤーy座標
    戻り値 degree: 角度(0~360)
    """
    radian = math.atan2(pl_y - pos_y, pl_x - pos_x)
    degree = radian * (180 / math.pi)
    return -degree


class Bullet(pg.sprite.Sprite):
    """
    弾に関するクラス
    """
    def __init__(self, pre_x, pre_y, pos_x, pos_y, attack_type=None):
        """
        弾を指定の場所から発射する関数
        引数1 pre_x: 中心x座標
        引数2 pre_y: 中心y座標
        引数3 pos_x: 発射するx座標
        引数4 pos_y: 発射するy座標
        """
        super().__init__()
        rad = 5
        self.image = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.image, (255, 255, 255), (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.centerx = pos_x
        self.rect.centery = pos_y
        self.speed = 1
        if attack_type:
            self.speed = 3
        self.vx, self.vy = calc_orientation(self.rect, pre_x, pre_y)

    def update(self):
        """
        弾を速度ベクトルself.vx, self.vyに基づき移動させる
        """
        move_x = +self.speed*self.vx
        move_y = +self.speed*self.vy
        # 速度小さすぎたら補正
        if -1 <= move_x <= 1:
            move_x *= 2
        if -1 <= move_y <= 1:
            move_y *= 2
        self.rect.move_ip(move_x, move_y)
        if check_out(self.rect) != (True, True):
            self.kill()

class PreBeam(pg.sprite.Sprite):
    """
    ビームを発射する起点の円に関するクラス
    """
    def __init__(self, pos_x, pos_y, pl_x, pl_y, tmr):
        """
        起点の円を描画する
        引数1 pos_x: 起点のx座標
        引数2 pos_y: 起点のy座標
        引数3 pl_x: プレイヤーのx座標
        引数4 pl_y: プレイヤーのy座標
        引数5 tmr: ゲーム内時間
        """
        super().__init__()
        self.start_time = tmr
        self.delay_time = self.start_time + 100
        self.beam_time = self.delay_time + 50
        self.image = pg.Surface((100, 100))
        pg.draw.circle(self.image, (255, 255, 255), (50, 50), 50)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (pos_x, pos_y)
        self.pl_x = pl_x
        self.pl_y = pl_y
        self.beam_flg = False
    
    def update(self, tmr, beams: pg.sprite.Group, dummy_beams: pg.sprite.Group):
        """
        ビーム継続時間を超えたらインスタンスを消去する関数
        引数1 tmr: ゲーム内時間
        引数2 beams: ビームのグループ
        引数3 dummy_beam: ダミービームのグループ
        """
        if self.delay_time <= tmr <= self.beam_time and not self.beam_flg:
            beam = Beam(self.rect.centerx, self.rect.centery, 
                        self.pl_x, self.pl_y, self.delay_time)
            dummy_beam = Dummy_beam(self.rect.centerx, self.rect.centery, 
                        self.pl_x, self.pl_y, self.delay_time)
            beams.add(beam)
            dummy_beams.add(dummy_beam)
            self.beam_flg = True
        elif self.beam_time <= tmr:
            self.kill()


class Beam(pg.sprite.Sprite):
    """
    ビームに関するクラス
    """
    def __init__(self, pos_x, pos_y, pl_x, pl_y, tmr):
        """
        起点からビームを生成する関数
        引数1 pos_x: 起点のx座標
        引数2 pos_y: 起点のy座標
        引数3 pl_x: プレイヤーのx座標
        引数4 pl_y: プレイヤーのy座標
        引数5 tmr: ゲーム内時間
        """
        super().__init__()
        self.image = pg.Surface((1600, 40))
        if pos_x < WIDTH/2:
            pg.draw.rect(self.image, (255, 255, 255), (800, 0, 800, 40))
        elif WIDTH/2 < pos_x:
            pg.draw.rect(self.image, (255, 255, 255), (800, 0, 800, 40))
        degree = calc_degree(pos_x, pos_y, pl_x, pl_y)
        self.image = pg.transform.rotozoom(self.image, degree, 1.0)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (pos_x, pos_y)
        self.mask = pg.mask.from_surface(self.image)
        self.beam_time = tmr + 50
        beam_sound = load_sound("ビーム砲2.mp3")
        if pg.mixer:
            beam_sound.set_volume(0.4)
            beam_sound.play()

    def update(self, tmr):
        """
        インスタンスを消去する関数
        引数1 tmr: ゲーム内時間
        """
        if self.beam_time <= tmr:
            self.kill()


class Dummy_beam(pg.sprite.Sprite):
    """
    ビームに関するクラス
    """
    def __init__(self, pos_x, pos_y, pl_x, pl_y, tmr):
        """
        起点からビームを生成する関数
        引数1 pos_x: 起点のx座標
        引数2 pos_y: 起点のy座標
        引数3 pl_x: プレイヤーのx座標
        引数4 pl_y: プレイヤーのy座標
        引数5 tmr: ゲーム内時間
        """
        super().__init__()
        self.image = pg.Surface((1600, 40))
        if pos_x < WIDTH/2:
            pg.draw.rect(self.image, (255, 255, 255), (800, 0, 800, 40))
        elif WIDTH/2 < pos_x:
            pg.draw.rect(self.image, (255, 255, 255), (800, 0, 800, 40))
        degree = calc_degree(pos_x, pos_y, pl_x, pl_y)
        self.image = pg.transform.rotozoom(self.image, degree, 1.0)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (pos_x, pos_y)
        self.beam_time = tmr + 50

    def update(self, tmr):
        """
        インスタンスを消去する関数
        引数1 tmr: ゲーム内時間
        """
        if self.beam_time <= tmr:
            self.kill()


def check_out_stage(obj: pg.Rect):
    """
    objがステージ外に出たかを判定する関数
    引数 obj: pg.Rect
    横方向 縦方向のはみ出し判定結果
    （ステージ内: True/ステージ外: False）
    """
    yoko, tate = True, True
    if obj.right < STAGE_LEFT or STAGE_RIGHT < obj.left:
        yoko = False
    if obj.bottom < STAGE_TOP or STAGE_BOTTOM < obj.top:
        tate = False
    return yoko, tate


def gen_rope_jump(air_y, pillars: pg.sprite.Group, dummy_pillars: pg.sprite.Group):
    """
    隙間のある4つの柱を生成する関数
    引数1 air_y: 空間のy座標
    引数2 pillars: 柱のグループ
    """
    gap = 20 # 隙間
    lst = [
        (STAGE_LEFT, STAGE_TOP, air_y - STAGE_TOP - gap, +1), # 左上
        (STAGE_LEFT, STAGE_BOTTOM, STAGE_BOTTOM - air_y - gap, +1), # 左下
        (STAGE_RIGHT, STAGE_TOP, air_y - STAGE_TOP - gap, -1), # 右上
        (STAGE_RIGHT, STAGE_BOTTOM, STAGE_BOTTOM - air_y - gap, -1) # 右下
    ]
    for arg in lst:
        pillar = Pillar(*arg)
        dummy_pillar = Dummy_pillar(*arg)
        pillars.add(pillar)
        dummy_pillars.add(dummy_pillar)


class Pillar(pg.sprite.Sprite):
    """
    柱に関するクラス
    """

    def __init__(self, pos_x, pos_y, height, vx ):
        """
        柱を生成する関数
        引数1 pos_x: 生成するx座標
        引数2 pos_y: 生成するy座標
        引数3 height: 柱の高さ
        引数4 vx: 横方向の移動量
        """
        super().__init__()
        self.image = pg.Surface((10, height))
        pg.draw.rect(self.image, (255, 255, 255), (0, 0, 10, height))
        self.rect = self.image.get_rect()
        self.rect.centerx = pos_x
        if pos_y == STAGE_TOP:
            self.rect.top = pos_y
        else:
            self.rect.bottom = pos_y
        self.vx = vx

    def update(self):
        """
        ステージ外に出たら消去
        """
        self.rect.centerx += self.vx
        if check_out_stage(self.rect) != (True, True):
            self.kill()


class Dummy_pillar(pg.sprite.Sprite):
    """
    柱に関するクラス
    """

    def __init__(self, pos_x, pos_y, height, vx ):
        """
        柱を生成する関数
        引数1 pos_x: 生成するx座標
        引数2 pos_y: 生成するy座標
        引数3 height: 柱の高さ
        引数4 vx: 横方向の移動量
        """
        super().__init__()
        self.image = pg.Surface((10, height))
        pg.draw.rect(self.image, (255, 255, 255), (0, 0, 10, height))
        self.rect = self.image.get_rect()
        self.rect.centerx = pos_x
        if pos_y == STAGE_TOP:
            self.rect.top = pos_y
        else:
            self.rect.bottom = pos_y
        self.vx = vx

    def update(self):
        """
        ステージ外に出たら消去
        """
        self.rect.centerx += self.vx
        if check_out_stage(self.rect) != (True, True):
            self.kill()



def main():
    clock = pg.time.Clock()
    if pg.mixer:
        music = os.path.join(main_dir, "data", "voice_50210.mp3")
        pg.mixer.music.load(music)
        pg.mixer.music.play(-1)
    emys = pg.sprite.Group()
    emys.add(Enemy())
    pg.display.set_caption("Under tale")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    sikaku1 = pg.Surface((400, 200))
    pg.draw.rect(sikaku1, (255, 255, 255), (0, 0, 400, 200))
    pg.draw.rect(sikaku1, (0, 0, 0), (5, 5, 390, 190))
    menu_sur = pg.Surface((600, 200))
    pg.draw.rect(menu_sur, (255, 255, 255), (0, 0, 600, 200))
    pg.draw.rect(menu_sur, (0, 0, 0), (5, 5, 590, 190))

    # テキストの文字色
    white = (255, 255, 255)
    yellow = (255, 205, 0)

    #　ここからhpクラスオブジェクトを生成
    hpbar_width = 100
    hpbar_sur = pg.Surface((250, 50)) # HPバーが表示される空間
    hp_HP = Hp()
    hp_HP.genfont("HP")
    hp_num = Hp()
    hp_num.genfont(f"{hpbar_width}/100")
    hp_bar_red = Hp()
    hp_bar_red.genobj((255, 0, 0), (50, 0, 100, 20), hpbar_sur)
    hp_bar_green = Hp()
    hp_bar_green.genobj((0, 255, 0), (50, 0, hpbar_width, 20), hpbar_sur)
    hp_bar_black = Hp()
    hp_bar_black.genobj((1, 1, 1), (170, 0, 100, 20), hpbar_sur)
    damage_txt = Hp()
    damage_txt.genfont("")
    #　ここまで
    attack_bar_lis = [10, 5] # インデックス０（表示するｘ座標）インデックス１（移動するｘ座標のピクセル量）
    attack_damage = 0 # プレイヤーの攻撃値を保持

    player = player_move((WIDTH/2, HEIGHT/2)) # プレイヤーメソッドを生成

    # 各種コマンドのメソッドを作成
    fight = Command("たたかう", 110, 470) # FIGHTコマンドの作成
    act = Command("こうどう", 290, 470)
    item = Command("アイテム", 475, 470)
    mercy = Command("みのがす", 670, 470)
    mode = "standard"
    cmd_select = 0

    # 説明文関係
    ex_1 = Explanation("")
    ex_2 = Explanation("")
    item1_stock = 5 
    item2_stock = 3
    ex_select = 0 # 説明文の選択状況
    friendly_point = 0 # 逃がすのに必要なポイント
    txt_number = 1
    action_txt_list = ["* ???のうごきがとまる", 
                       "* かなしみのひょうじょうが", "* やすらかなものとなり", 
                       "* そして", "* もといたところにかえっていく", ]

    turn_flag = True 
    processed = False

    bg = pg.Surface((WIDTH, HEIGHT)) 
    enemy_attack_count = 0
    enemy_hp = 300
    enemy_hp_bar_red = Hp()
    enemy_hp_bar_red.genobj((255, 0, 0), (200, 40, enemy_hp, 20), menu_sur)
    enemy_hp_bar_green = Hp()
    enemy_hp_bar_green.genobj((0, 255, 0), (200, 40, enemy_hp, 20), menu_sur)

    dead_flag = False
    enemy_dead_flag = False
    pressing = False
    attacked = False

    pressed_space = False
    jump_tmr = 0


    tmr = 0
    while True:
        key_lst = pg.key.get_pressed() # 入力キーを取得
        if hp_bar_green.width > 100:
            hp_bar_green.width = 100
        elif hp_bar_green.width < 0:
            hp_bar_green.width = 0
        hp_bar_green.locate = (50, 0, hp_bar_green.width, 20)
        if enemy_hp > 20:
            menu_txt = "* じっとこちらをみている"
        elif enemy_hp > 100:
            menu_txt = "* こわいかおでにらんでいる"
        elif enemy_hp > 30:
            menu_txt = "* いかり くるっている"
        elif 30 >= enemy_hp:
            menu_txt = "* どことなくかなしそうだ"
        if hp_bar_green.width < 30:
            menu_txt = "* ふてきなえみをうかべている"


        # 以下敵の攻撃用変数などを生成またはリセット
        if turn_flag and not processed:
            player.rect.center = [WIDTH/2, HEIGHT/2]
            gravity = False
            decision = False
            enemy_hp_bar_red.locate = (250, 40, 300, 20)
            enemy_hp_bar_green.locate = (250, 40, enemy_hp, 20)
            player.image = pg.transform.rotozoom(pg.image.load(f"ex05/fig/0.png"), 0, 0.02)
            attack_type = random.randint(0, 4)
            if attack_type == 4:
                player.image = pg.transform.rotozoom(pg.image.load(f"ex05/fig/1.png"), 0, 0.02)
               
            # 拡散弾幕用変数
            flowers = pg.sprite.Group()
            lin_cnt = 0
            lin_num = 14

            # 拡散弾幕（直線）
            FL_pre_x = 50
            line_y = [100, 150, 230, 250, 300, 340, 450]
            FL_pre_y = random.choice(line_y)

            # 自機狙い用変数
            atk_pl = pg.sprite.Group()
            area_out = True

            # ビーム用変数
            pre_beams = pg.sprite.Group()
            beams = pg.sprite.Group()
            dummy_beams = pg.sprite.Group()

            # ジャンプステージ用変数
            pillars = pg.sprite.Group()
            dummy_pillars = pg.sprite.Group()


            processed = True
    
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            
            if event.type == pg.KEYDOWN and event.key == pg.K_RIGHT and mode == "standard":
                if cmd_select == 3:
                    cmd_select = 3
                else:
                    cmd_select += 1
            if event.type == pg.KEYDOWN and event.key == pg.K_LEFT and mode == "standard":
                if cmd_select == 0:
                    cmd_select = 0
                else:
                    cmd_select -= 1

            if not(pressing) and event.type == pg.KEYDOWN and event.key == pg.K_RETURN and mode == "standard":
                pg.draw.rect(menu_sur, (0, 0, 0), (5, 5, 590, 190))
                if cmd_select == 0:
                    mode = "FIGHT"
                    ex_1.str = "* ???"
                    ex_select = 0
                if cmd_select == 1:
                    mode = "ACT"
                    ex_1.str = "* はなす"
                    ex_2.str = "* せっとく"
                    ex_select = 0
                if cmd_select == 2:
                    mode = "ITEM"
                    ex_1.str = f"* はとこうめグミ {item1_stock}"
                    ex_2.str = f"* みっくちゅジューチュ {item2_stock}"
                    ex_select = 0
                if cmd_select == 3:
                    mode = "MERCY"
                    ex_1.str = "* にげる"
                    ex_2.str = "* にがす"
                    ex_select = 0
                pressing = True

            if event.type == pg.KEYDOWN and event.key == pg.K_UP and (mode == "ITEM" or mode == "MERCY" or mode == "ACT"):
                    if not ex_select == 0:
                        ex_select -= 1

            if event.type == pg.KEYDOWN and event.key == pg.K_DOWN and (mode == "ITEM" or mode == "MERCY" or mode == "ACT"):
                    if not ex_select == 1:
                        ex_select += 1

            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE and not (mode == "standard" or mode == "ATTACK" or mode == "avoid" or mode == "TXT" or mode == "friendly"):
                mode = "standard"
                pg.draw.rect(menu_sur, (0, 0, 0), (5, 5, 590, 190))

            if event.type == pg.QUIT:
                return 0  
            
            if not(pressing) and event.type == pg.KEYDOWN and event.key == pg.K_RETURN and mode == "FIGHT":
                mode = "ATTACK"
                pressing = True

            if not(pressing) and event.type == pg.KEYDOWN and event.key == pg.K_RETURN and mode == "ITEM":
                cure_sound = load_sound("パワーアップ.mp3")
                if ex_select == 0:
                    if item1_stock > 0:
                        if pg.mixer:
                            cure_sound.play()
                        hp_bar_green.width += 50
                        item1_stock -= 1
                        mode = "avoid"

                elif ex_select == 1:
                    if item2_stock > 0:
                        if pg.mixer:
                            cure_sound.play()
                        hp_bar_green.width += 70
                        item2_stock -= 1
                        mode = "avoid"
                pressing = True
            
            if not(pressing) and event.type == pg.KEYDOWN and event.key == pg.K_RETURN and enemy_dead_flag and not(dead_flag):
                if action_txt == "* あなたのかち":
                    dead_flag = True
                action_txt = "* あなたのかち"


            if not(pressing) and event.type == pg.KEYDOWN and event.key == pg.K_RETURN and mode == "friendly":
                if txt_number < 6:
                    txt_number += 1
                else:
                    return
                pressing = True

            if not(pressing) and event.type == pg.KEYDOWN and event.key == pg.K_RETURN and mode == "friendly":
                txt_number += 1
                pressing = True

            if not(dead_flag) and not(pressing) and event.type == pg.KEYDOWN and event.key == pg.K_RETURN and mode == "TXT":
                if not enemy_dead_flag:
                    mode = "avoid"
                    pressing = True


            if not(pressing) and event.type == pg.KEYDOWN and event.key == pg.K_RETURN and mode == "MERCY":
                if ex_select == 0:
                    action_txt = "* ばかたれ　にげられるわけなか"
                    mode = "TXT"

                if ex_select == 1:
                    if friendly_point >= 200:
                        mode = "friendly"
                    else:
                        action_txt = "* そんなことをしているよゆうはない"
                        mode = "TXT"
                pressing = True

            if not(pressing) and event.type == pg.KEYDOWN and event.key == pg.K_RETURN and mode == "ACT":
                if ex_select == 0:
                    if friendly_point >= 180:
                        action_txt = "??? 「かえ..ら...なきゃ」"
                    elif 180 > friendly_point >= 160:
                        action_txt = "??? 「おもい..だした...」"
                    elif 160 > friendly_point >= 140:
                        action_txt = "??? 「お...かあ..さん」"
                    elif 140 > friendly_point >= 70:
                        action_txt = random.choice(["???「どうしてなの？」", "???「なんであなただけ！」", "???「あ...あたまが...」"])
                    else:
                        action_txt = random.choice(["???「いたい..いたい...」", "???「くるしい...」", "???「たす...たすけ..て」"])
                                     
                    friendly_point += random.choice([5, 10, 15, 20])
                    mode = "TXT"

                if ex_select == 1:
                    action_txt = random.choice(["* きくみみをもたない", "* さらににらまれた", "* すきがない", "* あっちょんぶりけ", "???「うるさい！」"])
                    if friendly_point >= 180:
                        action_txt = "「...」ひょうじょうがやわらいだ"
                    elif 180 > friendly_point >= 160:
                        action_txt = "「...」いかりがおさまったようだ"
                    elif 160 > friendly_point >= 140:
                        action_txt = "「...」どうようがみえる"
                    elif 140 > friendly_point >= 70:
                        action_txt = random.choice(["「...」かおがこわばった", "「...」すこしこんわくしている", "こうげきがはげしくなった"])
                    else:
                        action_txt = "「...」きくみみをもたない"
                          
                    
                    
                    friendly_point += random.choice([5, 10, 15, 20])
                    mode = "TXT"

                pressing = True

            # 攻撃値決定⇒敵の攻撃ターン
            if not(pressing) and event.type == pg.KEYDOWN and event.key == pg.K_RETURN and mode == "ATTACK":
                mode = "avoid"
                attack_damage = int(30-(abs((attack_bar_lis[0]-292)/10))) # プレイヤーの攻撃値決定
                attack_bar_lis = [10, 10] # attack_bar_lisをリセット
                screen.fill((0, 0, 0))
                enemy_hp -= attack_damage
                friendly_point -= 20
                attacked = True
                attack_tmr = tmr
                if enemy_hp < 0:
                    action_txt = "??? 「ありがとう」"
                    mode = "TXT"
                    enemy_dead_flag = True


            if player.on_the_ground:
                if event.type == pg.KEYDOWN and event.key == pg.K_SPACE and mode == "avoid" and attack_type == 4 and player.jump == False:
                    player.jump = True
                    player.on_the_ground = False
                    
                
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE and mode == "avoid" and attack_type == 4:
                pressed_space = True
                jump_tmr = 0
                

                

            if event.type == pg.KEYUP and event.key == pg.K_SPACE and mode == "avoid" and attack_type == 4:
                pressed_space = False
                flag = True
                jump_tmr = tmr

            if event.type == pg.KEYUP and event.key == pg.K_RETURN:
                pressing = False

            if not(pressing) and event.type == pg.KEYDOWN and event.key == pg.K_RETURN and dead_flag:
                return        
            
        if hp_bar_green.width <= 0:
            action_txt = "* だんだんめのまえがくらくなっていく"
            mode = "TXT"
            dead_flag = True

        if cmd_select == 0:
            fight.color_update((255, 205, 0))
        else:
            fight.color_update((255, 255, 255))
        if cmd_select == 1:
            act.color_update((255, 205, 0))
        else:
            act.color_update((255, 255, 255))
        if cmd_select == 2:
            item.color_update((255, 205, 0))
        else:
            item.color_update((255, 255, 255))
        if cmd_select == 3:
            mercy.color_update((255, 205, 0))
        else:
            mercy.color_update((255, 255, 255))

        if mode == "standard":
            pg.draw.rect(menu_sur, (0, 0, 0), (5, 5, 590, 190))
            ex_1.str = f"{menu_txt}"
            ex_1.color = white
            ex_1.update(menu_sur, [30, 30])

        if mode == "TXT":
            pg.draw.rect(menu_sur, (0, 0, 0), (5, 5, 590, 190))
            ex_1.str = f"{action_txt}"
            ex_1.color = white
            ex_1.update(menu_sur, [30, 30])

        if mode == "friendly":
            pg.draw.rect(menu_sur, (0, 0, 0), (5, 5, 590, 190))
            if txt_number == 6:
                ex_1.str = "* おうちへかえろう"
            else:
                ex_1.str = f"{action_txt_list[txt_number-1]}"
            ex_1.color = white
            ex_1.update(menu_sur, [30, 30])
                
            

        if mode == "ATTACK":
            attack_action(attack_bar_lis, menu_sur)

        if mode == "FIGHT":
            ex_1.color = yellow 
            ex_1.update(menu_sur, [30, 30])
            enemy_hp_bar_red.update(menu_sur)
            enemy_hp_bar_green.update(menu_sur)
            
        screen.blit(bg, (0, 0))
        if mode == "ACT": # 行動関係
            pg.draw.rect(menu_sur, (0, 0, 0), (5, 5, 590, 190))
            if ex_select == 0:   
                ex_1.color = yellow 
                ex_2.color = white         
                ex_1.update(menu_sur, [30, 30])
                ex_2.update(menu_sur, [30, 80])
                
            if ex_select == 1:
                ex_1.color = white 
                ex_2.color = yellow 
                ex_1.update(menu_sur, [30, 30])
                ex_2.update(menu_sur, [30, 80])

        if mode == "ITEM": # 行動関係
            pg.draw.rect(menu_sur, (0, 0, 0), (5, 5, 590, 190))
            if ex_select == 0:   
                ex_1.color = yellow 
                ex_2.color = white         
                ex_1.update(menu_sur, [30, 30])
                ex_2.update(menu_sur, [30, 80])
                
            if ex_select == 1:
                ex_1.color = white 
                ex_2.color = yellow 
                ex_1.update(menu_sur, [30, 30])
                ex_2.update(menu_sur, [30, 80])

        if mode == "MERCY": # 行動関係
            pg.draw.rect(menu_sur, (0, 0, 0), (5, 5, 590, 190))
            if friendly_point < 200:
                ex_select = 0

            if ex_select == 0:   
                ex_1.color = yellow 
                ex_2.color = white         
                ex_1.update(menu_sur, [30, 30])
                if friendly_point >= 200:
                    ex_2.update(menu_sur, [30, 80])
                
            if ex_select == 1:
                ex_1.color = white 
                ex_2.color = yellow 
                ex_1.update(menu_sur, [30, 30])
                if friendly_point >= 200:
                    ex_2.update(menu_sur, [30, 80])
        menu_sur.set_colorkey((0, 0, 0))
        screen.blit(menu_sur, (100, 200))

        if mode == "avoid":
            pg.draw.rect(bg, (0, 0, 0), (270, 100, 300, 100))
            emys.update(bg)
            if not decision:
                change_tmr = tmr
                decision = True
            if attacked:
                if tmr < attack_tmr + 100:
                    damage_txt.fonto = pg.font.Font(None, 90)
                    damage_txt.update(bg, (370, 100), f"{attack_damage}", (255, 0, 0))
                    enemy_hp_bar_red.locate = (270, 150, 300, 20)
                    enemy_hp_bar_green.locate = (270, 150, enemy_hp, 20)
                    enemy_hp_bar_red.update(bg)
                    enemy_hp_bar_green.update(bg)
            screen.blit(bg, (0, 0))
            
        if not mode == "avoid":
            emys.update(screen)

        #ここからhpクラスオブジェクトを更新
        hp_bar_black.update(hpbar_sur)
        hp_bar_red.update(hpbar_sur)
        hp_bar_green.update(hpbar_sur)
        hp_HP.update(hpbar_sur, [20, 5], "HP")
        hp_num.update(hpbar_sur, [170, 5], f"{hp_bar_green.width}/100")
        #　ここまで

        screen.blit(hpbar_sur, (250, 405)) # hpbar_surの表示位置の指定
        hpbar_sur.set_colorkey((0, 0, 0)) 
        fight.update(screen)
        act.update(screen)
        item.update(screen)
        mercy.update(screen)


        if mode == "avoid":
            screen.blit(sikaku1, (200, 200))
            if enemy_attack_count >= 20:
                enemy_attack_count = 0
                mode = "standard"
                processed = False

            if attack_type ==  0:
                if tmr % 40 == 0:
                    enemy_attack_count += 0.5
                    FR_pre_x = random.randint(50, WIDTH-50)
                    FR_pre_y = random.randint(100, 300)
                    flos = gen_flower(FR_pre_x, FR_pre_y)
                    for flo in flos:
                        flowers.add(flo)

            elif attack_type == 1:
                # 拡散弾幕（直線）
                if tmr % 20 == 0 and lin_cnt < lin_num:
                    flos = gen_flower(FL_pre_x, FL_pre_y)
                    for flo in flos:
                        flowers.add(flo)
                    FL_pre_x += 60
                    lin_cnt += 1
                elif lin_cnt >= lin_num:
                    FL_pre_x = 50
                    FL_pre_y = random.choice(line_y)
                    lin_cnt = 0
                    enemy_attack_count += 2


            elif attack_type == 2:
                # 自機狙い
                if tmr % 20 == 0:
                    enemy_attack_count += 0.2
                    area_out = True
                    while area_out:
                        SP_pos_x = random.randint(50, WIDTH-50)
                        SP_pos_y = random.randint(200, 400)
                        if SP_pos_x < 100 or WIDTH-100 < SP_pos_x:
                            area_out = False
                    SP_pre_x = player.rect[0]
                    SP_pre_y = player.rect[1]
                    atk_pl.add(Bullet(SP_pre_x, SP_pre_y, SP_pos_x, SP_pos_y, attack_type))

            elif attack_type == 3:
                # ビーム
                if tmr % 100 == 0:
                    enemy_attack_count += 1
                    area_out = True
                    while area_out:
                        pos_x = random.randint(50, WIDTH-50)
                        pos_y = random.randint(50, 500)
                        if not ((150 < pos_x < 650) and (150 < pos_y < 450)):
                            area_out = False
                    pl_x = player.rect[0]
                    pl_y = player.rect[1]
                    pre_beam = PreBeam(pos_x, pos_y, pl_x, pl_y, tmr)
                    pre_beams.add(pre_beam)

            elif attack_type == 4:
                gravity = True
                sin = 0
                if player.jump:
                    if pressed_space:
                        player.jump_tmr += 1
                        sin = 4.5-math.cos(math.radians(player.jump_tmr/2))*10
                        # if sin > 0:
                        #     sin = sin/2
                    if not pressed_space and tmr > jump_tmr + 30:
                        if flag:
                            if player.jump_tmr > 180:
                                player.jump_tmr = player.jump_tmr*-1
                            elif player.jump_tmr < 90:
                                player.jump_tmr = 180-player.jump_tmr
                            flag = False
                        player.jump_tmr += 1
                        sin = 4.5-math.cos(math.radians(player.jump_tmr)) * 10
                        # if sin > 0:
                        #     sin = sin/3
                sin = sin/2
                player.update(key_lst, screen, gravity, sin)
                # ジャンプステージ
                if tmr > change_tmr + 50:
                    if tmr % 200 == 0:
                        enemy_attack_count += 1.5
                        gen_rope_jump(random.randint(STAGE_TOP+25, STAGE_BOTTOM-25),pillars, dummy_pillars)
                # ステージの上下端からrandintすると高さが負の値になって、エラーが出ることがある
                # そのための余裕(+25, -25)
                # clock.tick(165)で作成
            
            if not gravity:
                player.update(key_lst, screen) # プレイヤーの表示位置を更新

            if len(pg.sprite.spritecollide(player, flowers, True)) != 0:
                hp_bar_green.width -= 2
                hit_sound = load_sound("ショット命中.mp3")
                if pg.mixer:
                    hit_sound.play()

            if len(pg.sprite.spritecollide(player, atk_pl, True)) != 0:
                hp_bar_green.width -= 5 
                hit_sound = load_sound("ショット命中.mp3")
                if pg.mixer:
                    hit_sound.play()

            if len(pg.sprite.spritecollide(player, pillars, True)) != 0:
                hp_bar_green.width -= 2
                hit_sound = load_sound("ショット命中.mp3")
                if pg.mixer:
                    hit_sound.play()

            for beam in beams:
                if pg.sprite.collide_mask(player, beam):
                    hp_bar_green.width -= 10
                    hit_sound = load_sound("ショット命中.mp3")
                    if pg.mixer:
                        hit_sound.play()
                    beam.kill()

            flowers.update()
            flowers.draw(screen)
            atk_pl.update()
            atk_pl.draw(screen)
            pre_beams.update(tmr, beams, dummy_beams)
            pre_beams.draw(screen)
            beams.update(tmr)
            beams.draw(screen)
            dummy_beams.update(tmr)
            dummy_beams.draw(screen)
            pillars.update()
            pillars.draw(screen)
            dummy_pillars.update()
            dummy_pillars.draw(screen)


        pg.display.update()
        tmr += 1
        clock.tick(165)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()