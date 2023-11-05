import math
import random
import time
import sys
import pygame as pg


WIDTH = 800
HEIGHT = 500


class player_move:
    # 押下キーと移動量の辞書
    delta={ pg.K_UP: (0, -5),#ハートが赤いときの辞書
            pg.K_DOWN: (0, 5),
            pg.K_LEFT: (-5, 0),
            pg.K_RIGHT: (+5, 0),
        }
    delta2={ pg.K_UP: (0, -2),#ハートが青いときの辞書
            pg.K_DOWN: (0, 0),
            pg.K_LEFT: (-1, 0),
            pg.K_RIGHT: (+1, 0),
        }
    rad_per_frame = 2 * math.pi / 40
    height = 70
    floor = 375

    def __init__(self, xy: tuple[float, float],ao):
        #aoが０なら赤いハートで１なら青いハートの画像を使う
        if ao==0:
            self.img = pg.transform.flip(
                pg.transform.rotozoom(
                    pg.image.load(f"ex05_yusuke/fig/0.png"),0,0.02),True, False)
        elif ao==1:
            self.img = pg.transform.flip(
                pg.transform.rotozoom(
                    pg.image.load(f"ex05_yusuke/fig/1.png"),0,0.02),True, False)
        self.rct = self.img.get_rect()
        self.rct.center = xy
        # 変更
        self.jump_flg = False
        self.frames = 0 # ジャンプ中のフレーム数

    def calc_y(self):
        # https://qiita.com/odanny/items/297f32a334c41410cc5d
        if self.rct.top > __class__.floor:
            self.rct.top = __class__.floor
            self.jump_flg = False
            self.time = 0

    def update(self,key_lst: list[bool],screen:pg.Surface, ao):
        sum_mv = [0, 0]

        for k, mv in __class__.delta.items():
            if ao and key_lst[pg.K_UP]:
                self.jump_flg = True
                if key_lst[k]:
                    sum_mv[0] += mv[0]
                    sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)

        #ハートが枠から出ないようにする
        if self.rct[1]<=205:#上
            self.rct[1]=205
        if self.rct[1]>=376:#した
            self.rct[1]=376
        if self.rct[0]>=578:#右
            self.rct[0]=578
        if self.rct[0]<=205:#左
            self.rct[0]=205
        screen.blit(self.img, self.rct)
#追加

def main():
    pg.display.set_caption("Under tale")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    sikaku1 = pg.Surface((400, 200))
    pg.draw.rect(sikaku1, (255, 255, 255), (0, 0, 400, 200))
    pg.draw.rect(sikaku1, (0, 0, 0), (5, 5, 390, 190))
    
    ##追加
    ao_flag=1
    if ao_flag==0:#ハートが赤の時は真ん中からスタート
        player = player_move((WIDTH/2, HEIGHT/2),ao_flag)
    elif ao_flag==1:#ハートが青の時地面からスタート
        player = player_move((WIDTH/2, 386),ao_flag)
    clock = pg.time.Clock()
    ##追加

    while True:
        screen.blit(sikaku1, (200, 200))    
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            
        ###追加
        key_lst = pg.key.get_pressed()
        player.update(key_lst, screen,ao_flag)
        pg.display.update()
        clock.tick(165)#動くの遅くする
        ###追加

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()