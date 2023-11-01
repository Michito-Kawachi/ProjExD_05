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
        self.speed = 2
        self.vx, self.vy = __class__.calc_orientation(self.rect, pre_x, pre_y)

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
        print(f"x:{-x_diff/norm}, y:{-y_diff/norm}")
        return -x_diff/norm, -y_diff/norm
    
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
                """
                変数1 pre_x: 中心x座標
                変数2 pre_x: 中心y座標
                変数3 pos_x: 発射するx座標
                変数4 pos_y: 発射するy座標
                """
                pre_x = random.randint(50, WIDTH-50)
                pre_y = 100
                num = 8
                flos = []
                for theta in range(0, 360, int(360/num)):
                    print(theta)
                    if theta == 0:
                        pos_x = pre_x + 10
                        pos_y = pre_y
                    elif 0 < theta < 90:
                        pos_x = pre_x + 10
                        pos_y = pre_y - 10
                    elif theta == 90:
                        pos_x = pre_x
                        pos_y = pre_y - 10
                    elif 90 < theta < 180:
                        pos_x = pre_x - 10
                        pos_y = pre_y - 10
                    elif theta == 180:
                        pos_x = pre_x - 10
                        pos_y = pre_y
                    elif 180 < theta < 270:
                        pos_x = pre_x - 10
                        pos_y = pre_y + 10
                    elif theta == 270:
                        pos_x = pre_x
                        pos_y = pre_y + 10
                    elif 270 < theta < 360:
                        pos_x = pre_x + 10
                        pos_y = pre_y + 10

                    flos.append(Enemy(pre_x, pre_y, pos_x, pos_y))
                for flo in flos:
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