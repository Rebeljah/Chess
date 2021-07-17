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
        self.piece_sprites = PieceSet(self)

    def draw(self):
        for row in range(8):
            for col in range(8):
                x = col * self.sq_size
                y = row * self.sq_size
                # draw current square
                color = 'dark slate gray' if (row + col) % 2 else 'beige'
                pg.draw.rect(self.image, color, (x, y, self.sq_size, self.sq_size))
                # draw piece at current square
                if piece := self.piece_sprites[row][col]:
                    self.image.blit(piece.image, (x, y, piece.size, piece.size))

        self.app.display.blit(self.image, self.rect)


class PieceSet(list):
    def __init__(self, board):
        self.board = board
        for row in range(8):
            self.append([])
            for col in range(8):
                if (piece_name := board.state.board[row][col]) != '--':
                    self[row].append(self.PieceSprite(self, (row, col), piece_name))
                else:
                    self[row].append(None)

    class PieceSprite:
        def __init__(self, set, board_pos, name):
            self.set = set
            self.board_pos = board_pos
            self.name = name
            self.size = set.board.sq_size
            self.image = self.load_image()

        def __repr__(self):
            return f"{self.name}{self.board_pos}"

        def load_image(self):
            piece_image = pg.image.load(f"images/{self.name}.png").convert_alpha()
            return pg.transform.scale(piece_image, (self.size, self.size))
