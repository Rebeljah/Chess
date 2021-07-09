import pygame as pg


class Board:
    def __init__(self, app):
        self.app = app
        self.sq_size = app.screen.get_size()[0] / 8

    def draw(self):
        for row in range(8):
            for col in range(8):
                color = 'slate gray' if (row+col)%2 else 'beige'
                x = col * self.sq_size
                y = row * self.sq_size
                pg.draw.rect(self.app.screen, color, (x, y, self.sq_size, self.sq_size))