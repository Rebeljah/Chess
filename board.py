import pygame as pg

import engine


class Board:
    def __init__(self, app):
        self.app = app
        self.image = pg.Surface((app.rect.w - 128, app.rect.h - 128))
        self.rect = self.image.get_rect(center=app.rect.center)
        self.dimension = 8
        self.sq_size = int(self.rect.w / self.dimension)

        self.state = engine.BoardState()
        self.pieces = PieceSet(self)


    def draw(self):
        for row in range(8):
            for col in range(8):
                x = col * self.sq_size
                y = row * self.sq_size
                is_dark = (row + col) % 2
                pg.draw.rect(self.image, 'dark slate gray' if is_dark else 'beige', (x, y, self.sq_size, self.sq_size))

        self.pieces.draw(self.image)

        self.app.display.blit(self.image, self.rect)


class PieceSet(pg.sprite.Group):
    def __init__(self, board):
        super().__init__()
        self.board = board
        self.build_set()

    def build_set(self):
        state = self.board.state.state_arr
        for row in range(8):
            for col in range(8):
                if state[row][col]:
                    name = state[row][col]
                    self.add(
                        self.Piece(self, (row, col), name,  topleft=(col*self.board.sq_size, row*self.board.sq_size))
                    )


    class Piece(pg.sprite.Sprite):
        def __init__(self, set, square, name, **rect_pos):
            super().__init__()
            self.name = name
            self.square = square
            self.size = set.board.sq_size
            self.image = self.load_image()
            self.rect = self.image.get_rect(**rect_pos)

        def load_image(self):
            piece_image = pg.image.load(f"images/{self.name}.png").convert_alpha()
            return pg.transform.scale(piece_image, (self.size, self.size))
