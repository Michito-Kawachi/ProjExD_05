import math
import os
import random
import time
import sys
import pygame as pg


WIDTH = 800
HEIGHT = 500
STAGE_TOP = 200
STAGE_BOTTOM = 400
STAGE_LEFT = 205
STAGE_RIGHT = 590
main_dir = os.path.split(os.path.abspath(__file__))[0]


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
    if obj.right < 0 or WIDTH < obj.left:
        yoko = False
    if obj.bottom < 0 or 400 < obj.bottom:
        tate = False
    return yoko, tate


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


def gen_rope_jump(air_y, pillars: pg.sprite.Group):
    """
    隙間のある4つの柱を生成する関数
    引数1 air_y: 空間のy座標
    引数2 pillars: 柱のグループ
    """
    gap = 15 # 隙間
    lst = [
        (STAGE_LEFT, STAGE_TOP, air_y - STAGE_TOP - gap, +1), # 左上
        (STAGE_LEFT, STAGE_BOTTOM, STAGE_BOTTOM - air_y - gap, +1), # 左下
        (STAGE_RIGHT, STAGE_TOP, air_y - STAGE_TOP - gap, -1), # 右上
        (STAGE_RIGHT, STAGE_BOTTOM, STAGE_BOTTOM - air_y - gap, -1) # 右下
    ]
    for arg in lst:
        pillar = Pillar(*arg)
        pillars.add(pillar)


class Bullet(pg.sprite.Sprite):
    """
    弾に関するクラス
    """
    def __init__(self, pre_x, pre_y, pos_x, pos_y):
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
            move_x *= 1.8
        if -1 <= move_y <= 1:
            move_y *= 1.8
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
        self.delay_time = self.start_time + 40
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
            beams.add(beam)
            dummy_beams.add(beam)
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
        self.image = pg.Surface((600, 40))
        pg.draw.rect(self.image, (255, 255, 255), (0, 0, 600, 40))
        degree = calc_degree(pos_x, pos_y, pl_x, pl_y)
        self.image = pg.transform.rotozoom(self.image, degree, 1.0)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        if pos_y < 240:
            if pos_x <= WIDTH/2:
                self.rect.topleft = (pos_x, pos_y)
            else:
                self.rect.topright = (pos_x, pos_y)
        else:
            if pos_x <= WIDTH/2:
                self.rect.bottomleft = (pos_x, pos_y)
            else:
                self.rect.bottomright = (pos_x, pos_y)
        self.beam_time = tmr + 50

    def update(self, tmr):
        """
        インスタンスを消去する関数
        引数1 tmr: ゲーム内時間
        """
        if self.beam_time <= tmr:
            self.kill()


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


class Arrow(pg.sprite.Sprite):
    """
    矢印攻撃に関するクラス
    """
    def __init__(self, theta, pos_x, pos_y):
        """
        初期化
        """
        super().__init__()
        self.image = pg.Surface((40, 20))
        pg.draw.line(self.image, (255, 255, 0), (0, 9), (30, 9), 5)
        pg.draw.polygon(self.image, (255, 255, 0), [(40, 10), (30, 0), (30, 20)])
        self.mask = pg.mask.from_surface(self.image)
        self.image = pg.transform.rotozoom(self.image, theta, 1.0)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = pos_x, pos_y
        if theta == 0:
            self.move_v = (+1, 0)
        elif theta == 90:
            self.move_v = (0, -1)
        elif theta == 180:
            self.move_v = (-1, 0)
        elif theta == 270:
            self.move_v = (0, +1)
    
    def update(self):
        self.rect.move_ip(self.move_v)
        if check_out(self.rect) != (True, True):
            self.kill()
        

class NoMovePL(pg.sprite.Sprite):
    """
    動かないプレイヤーに関するクラス
    """
    def __init__(self):
        super().__init__()
        filename = os.path.join(main_dir, "fig", "0.png")
        self.image = pg.transform.rotozoom(
            pg.image.load(filename),
            0,
            0.02
        )
        self.rect = self.image.get_rect()
        self.rect.center = WIDTH/2, HEIGHT/2


class Shield(pg.sprite.Sprite):
    """
    盾に関するクラス
    """ 
    # 元画像imgを生成
    img = pg.Surface((50, 50))   
    pg.draw.line(img, (70, 130, 180), (0, 0), (0, 50), 7)
    pg.draw.line(img, (70, 130, 180), (0, 50), (25, 25), 4)

    def __init__(self, pl_x, pl_y):
        """
        盾を初期化
        引数1 pl_x: プレイヤーのx座標
        引数2 pl_y: プレイヤーのy座標
        """
        super().__init__()
        self.image = __class__.img
        self.image.set_colorkey((0, 0, 0))
        self.mask = pg.mask.from_surface(self.img)
        self.rect = self.image.get_rect()
        self.rect.left = pl_x - 30
        self.rect.centery = pl_y
        self.dir = 0

    def update(self, key_lst: list[bool]):
        """
        キーに応じてimageを回転
        引数 key_lst: 押下されたキーのリスト[bool]
        """
        if key_lst[pg.K_LEFT]:
            self.dir = 0 # 左
        elif key_lst[pg.K_DOWN]:
            self.dir = 90 # 下
        elif key_lst[pg.K_RIGHT]:
            self.dir = 180 # 右
        elif key_lst[pg.K_UP]:
            self.dir = 270 # 上
        self.image = pg.transform.rotozoom(__class__.img, self.dir, 1.0)
        self.image.set_colorkey((0, 0, 0))


def main():
    pg.display.set_caption("Under tale")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    sikaku1 = pg.Surface((400, 200))
    bg = pg.Surface((800, 400))
    pg.draw.rect(sikaku1, (255, 255, 255), (0, 0, 400, 200))
    pg.draw.rect(sikaku1, (0, 0, 0), (5, 5, 390, 190))
    pg.draw.rect(bg, (0, 0, 0), (0, 0, WIDTH, 400))
    
    # 拡散弾幕用変数
    flowers = pg.sprite.Group()
    delay_time = 15
    line_flag = False
    lin_cnt = 0
    lin_num = 10
    tmr = 0

    # 自機狙い用変数
    atk_pl = pg.sprite.Group()

    # ビーム用変数
    pre_beams = pg.sprite.Group()
    beams = pg.sprite.Group()
    dummy_beams = pg.sprite.Group()

    # ジャンプステージ用変数
    pillars = pg.sprite.Group()

    # 矢印用変数
    arrows = pg.sprite.Group()

    # 自機
    no_move = NoMovePL()
    shields = pg.sprite.Group()
    shields.add(Shield(no_move.rect.centerx, no_move.rect.centery))
    
    clock = pg.time.Clock()

    while True:
        screen.blit(bg, (0, 0))
        screen.blit(sikaku1, (200, 200))
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_q):
                return 0
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                # 拡散弾幕（ランダム）
                FR_pre_x = random.randint(50, WIDTH-50)
                FR_pre_y = random.randint(100, 300)
                flos = gen_flower(FR_pre_x, FR_pre_y)
                for flo in flos:
                    flowers.add(flo)

            elif event.type == pg.KEYDOWN and event.key == pg.K_LSHIFT:
                # 拡散弾幕（直線）
                FL_pre_x = 50
                line_y = [100, 200, 250, 300]
                FL_pre_y = random.choice(line_y)
                line_flag = True
                start_time = tmr
            
            elif event.type == pg.KEYDOWN and event.key == pg.K_TAB:
                # 自機狙い
                SP_pos_x = random.randint(50, WIDTH-50)
                SP_pos_y = random.randint(150, 300)
                SP_pre_x = WIDTH/2
                SP_pre_y = HEIGHT/2
                atk_pl.add(Bullet(SP_pre_x, SP_pre_y, SP_pos_x, SP_pos_y))
            
            elif event.type == pg.KEYDOWN and event.key == pg.K_a:
                # ビーム
                pos_x = random.randint(100, 700)
                pos_y = 235
                pl_x = WIDTH/2
                pl_y = HEIGHT/2
                pre_beam = PreBeam(pos_x, pos_y, pl_x, pl_y, tmr)
                pre_beams.add(pre_beam)

            elif event.type == pg.KEYDOWN and event.key == pg.K_w:
                # ジャンプステージ
                gen_rope_jump(random.randint(STAGE_TOP+25, STAGE_BOTTOM-25),pillars)
                # ステージの上下端からrandintすると高さが負の値になって、エラーが出ることがある
                # そのための余裕(+25, -25)
                # clock.tick(165)で作成
            
            elif event.type == pg.KEYDOWN and event.key == pg.K_z:
                arrow = Arrow(0, 100, 300)
                arrows.add(arrow)
            elif event.type == pg.KEYDOWN and event.key == pg.K_x:
                arrow = Arrow(90, WIDTH/2, 350)
                arrows.add(arrow)
            elif event.type == pg.KEYDOWN and event.key == pg.K_c:
                arrow = Arrow(180, 700, 300)
                arrows.add(arrow)
            elif event.type == pg.KEYDOWN and event.key == pg.K_v:
                arrow = Arrow(270, 400, 50)
                arrows.add(arrow)

        # 拡散弾幕（直線）
        if line_flag and tmr == start_time + delay_time * lin_cnt and lin_cnt <= lin_num:
            flos = gen_flower(FL_pre_x, FL_pre_y)
            for flo in flos:
                flowers.add(flo)
            FL_pre_x += 40
            lin_cnt += 1
        elif lin_cnt >= lin_num:
            lin_cnt = 0
            line_flag = False
                    
        key_lst = pg.key.get_pressed() # 入力キーを取得
        tmr += 1
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
        arrows.update()
        arrows.draw(screen)
        shields.update(key_lst)
        shields.draw(screen)
        # テスト用ダミー
        screen.blit(no_move.image, no_move.rect)

        pg.display.update()
        clock.tick(165)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()