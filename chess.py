import cProfile

import pygame as pg
import sys

import ui
import engine
import ai


class Chess:
    def __init__(self, mode='pvp'):
        self.clock = pg.time.Clock()
        self.display = pg.display.set_mode((680, 680))
        self.rect = self.display.get_rect()

        self.mode = mode
        self.board_state = engine.BoardState(self)
        self.board_ui = ui.BoardUI(self)
        self.minimax = ai.MiniMax(self.board_state)

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
                    self.board_state.undo_move(move=None, swap_tuns=True, regenerate_moves=True)

    def draw(self):
        self.display.fill('pink')
        self.board_ui.draw()
        pg.display.flip()


if __name__ == '__main__':
    chess = Chess(mode='pvp')
    chess.run()
    # cProfile.run("chess.board_state.move_generator.test()")
