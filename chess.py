import pygame as pg


class Chess:
    def __init__(self):
        self.screen = pg.display.set_mode((500, 500), pg.RESIZABLE)
        self.clock = pg.time.Clock()
    
    def run(self):
        while True:
            self.clock.tick(24)
            self.check_events()
            self.update()
            self.draw()

    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()

    def update(self):
        pass

    def draw(self):
        pass


if __name__ == '__main__':
    chess = Chess()
    chess.run()