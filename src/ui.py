import pygame as pg
import os

from constants import Color as color


class BoardUI:
    def __init__(self, app):
        self.app = app
        self.board_state = app.board_state

        self.image = pg.Surface((app.rect.w, app.rect.h)).convert_alpha()
        self.rect = self.image.get_rect(center=app.rect.center)
        self.sq_size = int(self.rect.w / 8)

        self.input = self.BoardInput(self)
        self.piece_images: dict = self.load_pieces()

    def load_pieces(self):
        pieces = {}
        image_dir = 'src/images/pieces'
        for name, ext in [fn.split('.') for fn in os.listdir(image_dir)]:
            fn = f"{image_dir}/{name}.{ext}"
            img = pg.transform.scale(pg.image.load(fn), (self.sq_size, self.sq_size)).convert_alpha()
            pieces.update({name: img})
        return pieces

    def draw(self):
        self.draw_board()
        self.draw_highlights()
        self.draw_pieces()
        self.app.display.blit(self.image, self.rect)

    def draw_board(self):
        for row in range(8):
            for col in range(8):
                x = col * self.sq_size
                y = row * self.sq_size
                # draw current square
                rgb = color.DARK if (row + col) % 2 else color.LIGHT
                self.image.fill(rgb, (x, y, self.sq_size, self.sq_size))

    def draw_highlights(self):
        for move in self.board_state.get_moves_of_square(self.input.from_pos):
            y, x = move.to_pos
            x *= self.sq_size
            y *= self.sq_size
            pg.draw.circle(self.image, 'red', (x+self.sq_size//2, y+self.sq_size//2), self.sq_size//5)

    def draw_pieces(self):
        for row in range(8):
            for col in range(8):
                square = self.board_state.get_piece(row, col)
                x = col * self.sq_size
                y = row * self.sq_size
                # draw pieces
                if square != '--':
                    image = self.piece_images[square]
                    """if self.app.mode == 'pvp' and square[0] == 'b':
                        image = pg.transform.rotate(image, 180)"""
                    self.image.blit(image, (x, y))


    class BoardInput:
        def __init__(self, board_ui):
            self.board = board_ui
            self.app = board_ui.app
            self.board_state = board_ui.app.board_state

            self.move_started = False
            self.from_pos = None

        def player_click(self):
            x, y = pg.mouse.get_pos()
            square_clicked = (y // self.board.sq_size, x // self.board.sq_size)

            if (not self.move_started) and (square_clicked in self.board_state.get_movable_squares()):
                # start a move
                self.move_started = True
                self.from_pos = square_clicked
            else:
                # make move
                for move in self.board_state.get_moves_of_square(self.from_pos):
                    if move.to_pos == square_clicked:
                        self.board_state.move_maker.apply_move(move)
                        break
                # End move
                self.move_started = False
                self.from_pos = None
