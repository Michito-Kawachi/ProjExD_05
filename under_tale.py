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
    def __init__(self, pos_x: int, pos_y: int):
        """
        弾を生成する
        引数1 pos_x: 弾が出るx座標
        引数2 pos_y: 弾が出るy座標
        """
        super().__init__()

        rad = 5
        self.image = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.image, (255, 255, 255), (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.speed = 1
        #self.vx, self.vy = __class__.calc_orientation(self.rect, pos_x-10, pos_y-10)
        self.vx = 2
        self.vy = 3
        self.rect.centerx = pos_x
        self.rect.centery = pos_y

    def check_out(obj: pg.Rect):
        """
        弾が画面外に出たかを判定する関数
        引数 obj: 弾のRect
        横方向 縦方向のはみ出し判定結果
        （画面内: True/画面外: False）
        """
        yoko, tate = True, True
        if obj.right < 0 or obj.left > WIDTH:
            yoko = False
        if obj.bottom < 0 or obj.bottom > 400:
            tate = False
        return yoko, tate
    
    def calc_orientation(org: pg.Rect, pos_x, pos_y) -> tuple[float, float]:
        """
        orgから見て, pos_x, pos_yがどこにあるかを計算し, 方向ベクトルをタプルで返す
        引数1 org: 爆弾SurfaceのRect
        引数2 pos_x: 目標のx座標
        引数3 pos_y: 目標のy座標
        戻り値: orgから見た目標の方向ベクトルを表すタプル
        """
        x_diff, y_diff = pos_x-org.centerx, pos_y-org.centery
        norm = math.sqrt(x_diff**2+y_diff**2)
        return -x_diff/norm, -y_diff/norm

    def flower(self, pos_x, pos_y):
        """
        拡散弾を作る関数
        引数 pos_x: x座標, pos_y: y座標
        """
        self.lst = []
        origin_x = random.randint(50, 750)
        #origin_x = 
    
    def beam(self, pos_x, pos_y):
        """
        直線の3連弾を作る関数
        引数1 pos_x: 原点x座標
        引数2 pos_y: 原点y座標
        """
        pass
    
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
    

    enemies= pg.sprite.Group()
    tmr = 0
    clock = pg.time.Clock()

    while True:
        screen.blit(bg, (0, 0))
        screen.blit(sikaku1, (200, 200))
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
        tmr += 1
        if 3<tmr%60<15:
            enemies.add(Enemy(20, 20))
        
        enemies.update()
        enemies.draw(screen)

        pg.display.update()
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()