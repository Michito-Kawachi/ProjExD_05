


class Enemy(pg.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.img =  pg.transform.scale(pg.image.load("ex0