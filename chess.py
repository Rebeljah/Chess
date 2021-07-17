import pygame as pg
import sys

import board
import engine


class Chess:
    def __init__(self):
        self.clock = pg.time.Clock()
        self.display = pg.display.set_mode((688, 688))
        self.rect = self.display.get_rect()

        self.board = board.Board(self)
    
    def run(self):
        while True:
            self.clock.tick(12)
            self.check_events()
            self.draw()

    def check_events(self):
        self.mouse_pos = pg.mouse.get_pos()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()

    def draw(self):
        self.display.fill('dark green')
        self.board.draw()
        pg.display.flip()

if __name__ == '__main__':
    chess = Chess()
    chess.run()
