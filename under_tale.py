import math
import random
import time
import sys
import pygame as pg


WIDTH = 800
HEIGHT = 500


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
    def __init__(self, pos_x, pos_y, tmr):
        """
        起点の円を描画する
        引数1 pos_x: 起点のx座標
        引数2 pos_y: 起点のy座標
        引数3 tmr: ゲーム内時間
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

    def get_delay_time(self):
        return self.delay_time
    
    def get_beam_time(self):
        return self.beam_time
    
    def get_pos(self):
        return self.rect.centerx, self.rect.centery
    
    def update(self, tmr):
        """
        ビーム継続時間を超えたらインスタンスを消去する関数
        引数1 tmr: ゲーム内時間
        """
        if self.beam_time <= tmr:
            self.kill()


class Beam(pg.sprite.Sprite):
    """
    ビームに関するクラス
    """
    def __init__(self, pos_x, pos_y, pl_x, pl_y):
        """
        起点からビームを生成する関数
        引数1 pos_x: 起点のx座標
        引数2 pos_y: 起点のy座標
        引数3 beam_time: ビームの継続時間
        """
        super().__init__()
        self.image = pg.Surface((600, 40))
        pg.draw.rect(self.image, (255, 255, 255), (0, 0, 600, 40))
        degree = calc_degree(pos_x, pos_y, pl_x, pl_y)
        self.image = pg.transform.rotozoom(self.image, degree, 1.0)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        if pos_x <= WIDTH/2:
            self.rect.topleft = (pos_x, pos_y)
        else:
            self.rect.topright = (pos_x, pos_y)

    def update(self, tmr, beam_time):
        """
        インスタンスを消去する関数
        引数1 tmr: ゲーム内時間
        引数2 beam_time: ビームの持続時間
        """
        if beam_time <= tmr:
            self.kill()
        

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

    # テスト用自機狙い用ダミーSurface
    pl = pg.Surface((20, 20))
    pg.draw.circle(pl, (255, 0, 0), (10, 10), 20)
    pl_rct = pl.get_rect()

    # ビーム用変数
    pre_beams = pg.sprite.Group()
    beams = pg.sprite.Group()
    fal_beams = pg.sprite.Group()
    pre_beam = None
    beam = None
    prebeam_flg = False
    beam_flg = False
    beam_time = 0
    
    clock = pg.time.Clock()

    while True:
        screen.blit(bg, (0, 0))
        screen.blit(sikaku1, (200, 200))
        for event in pg.event.get():
            if event.type == pg.QUIT:
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
                pos_x = 600
                pos_y = 100
                pl_x = WIDTH/2
                pl_y = HEIGHT/2
                pre_beam = PreBeam(pos_x, pos_y, tmr)
                pre_beams.add(pre_beam)
                prebeam_flg = True
                beam_flg = True
                beam_time = pre_beam.get_beam_time()

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

        # ビーム
        if prebeam_flg:
            if pre_beam.get_delay_time() <= tmr <= pre_beam.get_beam_time() and beam_flg :
                B_pos_x, B_pos_y = pre_beam.get_pos()
                beam = Beam(B_pos_x, B_pos_y, pl_x, pl_y)
                beams.add(beam)
                fal_beams.add(beam)
                beam_flg = False
            elif pre_beam.get_beam_time() <= tmr:
                beam_flg = False
                    
        tmr += 1
        flowers.update()
        flowers.draw(screen)
        atk_pl.update()
        atk_pl.draw(screen)
        pre_beams.update(tmr)
        pre_beams.draw(screen)
        beams.update(tmr, beam_time)
        beams.draw(screen)
        fal_beams.update(tmr, beam_time)
        fal_beams.draw(screen)
        # テスト用ダミー
        screen.blit(pl,(WIDTH/2, HEIGHT/2))

        pg.display.update()
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()