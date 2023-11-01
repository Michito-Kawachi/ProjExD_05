import math
import random
import time
import sys
import pygame as pg


WIDTH = 800
HEIGHT = 500


class Enemy(pg.sprite.Sprite):
    """
    敵の攻撃に関するクラス
    """
    def __init__(self, type: str):
        """
        どの弾幕を生成するか判定する関数
        引数1 type: 弾幕の種類（文字列）
        """
        super().__init__()
        self.lst = []
        if type == "flower":
            """
            変数1 pre_x: 中心x座標
            変数2 pre_x: 中心y座標
            変数3 pos_x: 発射するx座標
            変数4 pos_y: 発射するy座標
            """
            self.pre_x = random.randint(50, WIDTH-50)
            self.pre_y = 100
            self.num = 8
            for theta in range(0, 360, int(360/self.num)):
                if theta == 0:
                    self.pos_x = self.pre_x + 10
                    self.pos_y = self.pre_y
                elif 0 < theta < 90:
                    self.pos_x = self.pre_x + 10
                    self.pos_y = self.pre_y - 10
                elif theta == 90:
                    self.pos_x = self.pre_x
                    self.pos_y = self.pre_y - 10
                elif 90 < theta < 180:
                    self.pos_x = self.pre_x - 10
                    self.pos_y = self.pre_y - 10
                elif theta == 180:
                    self.pos_x = self.pre_x - 10
                    self.pos_y = self.pre_y
                elif 180 < theta < 270:
                    self.pos_x = self.pre_x - 10
                    self.pos_y = self.pre_y + 10
                elif theta == 270:
                    self.pos_x = self.pre_x
                    self.pos_y = self.pre_y + 10
                elif 270 < theta < 360:
                    self.pos_x = self.pre_x + 10
                    self.pos_y = self.pre_y + 10
                print(f"pos_x = {self.pos_x}, pos_y = {self.pos_y}")
                print(f"pre_x = {self.pre_x}, pre_y = {self.pre_y}")
                print("------")
                self.lst.append(__class__.gen_bul(self))

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
        return -x_diff/norm, -y_diff/norm

    def gen_bul(self):
        """
        弾を指定の場所から発射する関数
        """
        rad = 5
        self.image = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.image, (255, 255, 255), (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.centerx = self.pos_x
        self.rect.centery = self.pos_y
        self.speed = 1
        self.vx, self.vy = __class__.calc_orientation(self.rect, self.pre_x, self.pre_y)
        
        return self
    
    def update(self):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        """
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)
        if __class__.check_out(self.rect) != (True, True):
            self.kill()


def main():
    pg.display.set_caption("Under tale")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    sikaku1 = pg.Surface((400, 200))
    bg = pg.Surface((800, 400))
    pg.draw.rect(sikaku1, (255, 255, 255), (0, 0, 400, 200))
    pg.draw.rect(sikaku1, (0, 0, 0), (5, 5, 390, 190))
    pg.draw.rect(bg, (0, 0, 0), (0, 0, WIDTH, 400))
    

    flowers = pg.sprite.Group()
    tmr = 0
    clock = pg.time.Clock()

    while True:
        screen.blit(bg, (0, 0))
        screen.blit(sikaku1, (200, 200))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                flos = Enemy("flower")
                for flo in flos.lst:
                    if not flo == None:
                        flowers.add(flo)
        tmr += 1
        
        
        flowers.update()
        flowers.draw(screen)

        pg.display.update()
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()