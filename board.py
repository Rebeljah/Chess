import pygame as pg
import os

import engine


class Board:
    def __init__(self, app):
        self.app = app
        self.image = pg.Surface((app.rect.w, app.rect.h)).convert_alpha()
        self.rect = self.image.get_rect(center=app.rect.center)
        self.sq_size = int(self.rect.w / 8)

        self.state = engine.BoardState()
        self.piece_mover = PieceMover(self)
        self.pieces: dict = self.load_pieces()
        self.highlighted_moves = []

    def load_pieces(self):
        pieces = {}
        for name, ext in [fn.split('.') for fn in os.listdir('images/pieces')]:
            fn = f"{'images/pieces'}/{name}.{ext}"
            img = pg.transform.scale(pg.image.load(fn), (self.sq_size, self.sq_size)).convert_alpha()
            """if name[0] == 'b':
                img = pg.transform.rotate(img, 180)"""
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
                color = (92, 88, 76,255) if (row + col) % 2 else (255, 245, 214,255)
                self.image.fill(color, (x, y, self.sq_size, self.sq_size))

    def draw_highlights(self):
        for row, col in self.highlighted_moves:
            x = col * self.sq_size
            y = row * self.sq_size
            pg.draw.circle(self.image, 'yellow', (x+self.sq_size//2, y+self.sq_size//2), self.sq_size//4)

    def draw_pieces(self):
        for row in range(8):
            for col in range(8):
                x = col * self.sq_size
                y = row * self.sq_size
                # draw pieces
                if (piece := self.state.arr[row][col]) != 'empty':
                    self.image.blit(self.pieces[piece.name], (x, y))


class PieceMover:
    def __init__(self, board):
        self.board = board

        self.move_started = False
        self.from_pos = None
        self.to_pos = None

    def handle_click(self):
        mouse_x, mouse_y = pg.mouse.get_pos()
        r = mouse_y // self.board.sq_size
        c = mouse_x // self.board.sq_size
        if (not self.move_started) and ((r,c) in self.board.state.valid_moves.keys()):
            self.start_move(r, c)
        else:
            self.end_move(r, c)
    
    def start_move(self, r, c):
        self.move_started = True
        self.from_pos = (r, c)
        self.board.highlighted_moves.extend(self.board.state.valid_moves.get((r, c), []))

    def end_move(self, r, c):
        self.move_started = False
        if (r, c) in self.board.highlighted_moves:
            self.to_pos = (r, c)
            self.board.state.arr[self.from_pos[0]][self.from_pos[1]].move_piece(self.from_pos, self.to_pos)
            self.board.state.swap_turns()
        self.board.highlighted_moves.clear()