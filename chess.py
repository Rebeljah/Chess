import pygame as pg
import sys

import settings
import board
import engine


class EventManager:
    def __init__(self, app):
        self.app = app
        self.mouse_pos = None

    def check_events(self):
        self.mouse_pos = pg.mouse.get_pos()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            elif event.type == pg.WINDOWRESIZED:
                pass


class Chess:
    def __init__(self):
        self.vars = settings.Settings()
        self.clock = pg.time.Clock()
        self.event_manager = EventManager(self)
        self.screen = pg.display.set_mode((512, 512), pg.RESIZABLE)

        self.board = board.Board(self)
    
    def run(self):
        while True:
            self.clock.tick(self.vars.MAX_FPS)
            self.event_manager.check_events()
            self.update()
            self.draw()

    def update(self):
        pass

    def draw(self):
        self.board.draw()
        pg.display.flip()

if __name__ == '__main__':
    chess = Chess()
    chess.run()
