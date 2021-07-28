import pygame as pg
import sys

import ui
import engine


class Chess:
    def __init__(self):
        self.clock = pg.time.Clock()

        self.display = pg.display.set_mode((680, 680))
        pg.display.set_caption('PyChess')
        pg.display.set_icon(pg.image.load('src/images/icon.png').convert_alpha())

        self.rect = self.display.get_rect()

        self.engine = engine.Engine(self)
        self.board_ui = ui.BoardUI(self)

    def run(self):
        while True:
            self.clock.tick(12)
            self.check_events()
            self.draw()

    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                self.board_ui.input.player_click()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_z:
                    self.engine.move_maker.apply_move(is_undo=True)  # undo the last move taken

    def draw(self):
        self.board_ui.draw()
        pg.display.flip()


if __name__ == '__main__':
    chess = Chess()
    chess.run()
    # cProfile.run("src.board_state.move_generator.test()")
