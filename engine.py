import time
from copy import deepcopy

class Piece:
    def __init__(self, state, color, type):
        self.state = state
        self.color = color
        self.type = type
        self.name = self.color + self.type
        
        self.move_count = 0

    def __eq__(self, other):
        return self.__repr__() == str(other)

    def __repr__(self):
        return self.color + self.type  # wp

    def get_moves(self):
        pass
    
    def move_piece(self, from_pos, to_pos) -> None:
        if from_pos != to_pos:
            from_r, from_c = from_pos
            to_r, to_c = to_pos
            self.state.arr[to_r][to_c] = self
            self.state.arr[from_r][from_c] = Empty()

class K(Piece):
    def __init__(self, state, color):
        super().__init__(state, color, 'k')

    def get_moves(self, row, col):
        moves = []
        r, c = row, col
        possible = [(r - 1, c), (r - 1, c + 1), (r, c + 1), (r + 1, c + 1), (r + 1, c), (r + 1, c - 1), (r, c - 1),
                    (r - 1, c - 1)]
        for r, c in possible:
            if (
                (0 <= r <= self.state.max_index) and (0 <= c <= self.state.max_index)
                    and self.state.arr[r][c].color != self.state.curr_turn
            ): moves.append((r, c))
        return moves

class N(Piece):
    def __init__(self, state, color):
        super().__init__(state, color, 'n')

    def get_moves(self, r, c):
        moves = []
        possible = [(r - 1, c - 2), (r + 1, c - 2), (r - 2, c - 1), (r - 2, c + 1), (r - 1, c + 2), (r + 1, c + 2),
                    (r + 2, c + 1), (r + 2, c - 1)]
        for r, c in possible:
            if (
                (0 <= r <= self.state.max_index) and (0 <= c <= self.state.max_index)
                and (self.state.arr[r][c].color != self.state.curr_turn)
            ): moves.append((r, c))
        return moves

class Q(Piece):
    def __init__(self, state, color):
        super().__init__(state, color, 'q')
    
    def get_moves(self, row, col):
        moves = []
        for r_step, c_step in ((-1, 0), (0, 1), (1, 0), (0, -1), (-1, -1), (-1, 1), (1, 1), (1, -1)):
            r, c = row, col
            while (0 <= (r := r + r_step) <= self.state.max_index) and (0 <= (c := c + c_step) <= self.state.max_index):
                if (piece := self.state.arr[r][c]) == 'empty':
                    moves.append((r, c))
                elif piece.color == self.state.last_turn:
                    moves.append((r, c))
                    break
                else:
                    break
        return moves

class B(Piece):
    def __init__(self, state, color):
        super().__init__(state, color, 'b')
    
    def get_moves(self, row, col):
        moves = []
        for r_step, c_step in ((-1, -1), (-1, 1), (1, 1), (1, -1)):
            r, c = row, col
            while (0 <= (c := c+c_step) <= self.state.max_index) and (0 <= (r := r+r_step) <= self.state.max_index):
                if (piece := self.state.arr[r][c]) == 'empty':
                    moves.append((r, c))
                elif piece.color != self.state.curr_turn:
                    moves.append((r, c))
                    break
                else:
                    break
        return moves
    
class R(Piece):
    def __init__(self, state, color):
        super().__init__(state, color, 'r')
    
    def get_moves(self, row ,col):
        moves = []
        for r_step, c_step in ((-1, 0), (0, 1), (1, 0), (0, -1)):
            r, c = row, col
            while (0 <= (r := r+r_step) <= self.state.max_index) and (0 <= (c := c+c_step) <= self.state.max_index):
                if (piece := self.state.arr[r][c]) == 'empty':
                    moves.append((r, c))
                elif piece.color == self.state.last_turn:
                    moves.append((r, c))
                    break
                else:
                    break
        return moves

class P(Piece):
    def __init__(self, state, color):
        super().__init__(state, color, 'p')

        if self.color == 'w':
            self.step = -1
        else:
            self.step = 1

    def get_moves(self, row, col) -> list:
        moves = []
        r = row + self.step
        if 0 <= r <= self.state.max_index:
            # forward movement
            if self.state.arr[r][col] == 'empty':
                moves.append((r, col))
                if self.move_count == 0 and self.state.arr[r + self.step][col] == 'empty':
                    moves.append((r + self.step, col))
            # diagonal movement
            if (c := col - 1) >= 0:
                if self.state.arr[r][c].color == self.state.last_turn:
                    moves.append((r, c))
            if (c := col + 1) <= self.state.max_index:
                if self.state.arr[r][c].color == self.state.last_turn:
                    moves.append((r, c))
        return moves

class Empty(Piece):
    def __init__(self, state=None, color=''):
        super().__init__(state, color, 'empty')


class BoardState:
    def __init__(self):
        s = self
        self.arr = [
            [R(s, 'b'), N(s, 'b'), B(s, 'b'), Q(s, 'b'), K(s, 'b'), B(s, 'b'), N(s, 'b'), R(s, 'b')],
            [P(s, 'b'), P(s, 'b'), P(s, 'b'), P(s, 'b'), P(s, 'b'), P(s, 'b'), P(s, 'b'), P(s, 'b')],
            [Empty(), Empty(), Empty(), Empty(), Empty(), Empty(), Empty(), Empty()],
            [Empty(), Empty(), Empty(), Empty(), Empty(), Empty(), Empty(), Empty()],
            [Empty(), Empty(), Empty(), Empty(), Empty(), Empty(), Empty(), Empty()],
            [Empty(), Empty(), Empty(), Empty(), Empty(), Empty(), Empty(), Empty()],
            [P(s, 'w'), P(s, 'w'), P(s, 'w'), P(s, 'w'), P(s, 'w'), P(s, 'w'), P(s, 'w'), P(s, 'w')],
            [R(s, 'w'), N(s, 'w'), B(s, 'w'), Q(s, 'w'), K(s, 'w'), B(s, 'w'), N(s, 'w'), R(s, 'w')]
        ]

        self.max_index = len(self.arr) - 1
        self.curr_turn = 'w'
        self.last_turn = 'b'
        self.valid_moves = {}
        self.get_valid_moves()

        tests = []
        for test in range(31**2):
            start = time.time()
            state = deepcopy(self)
            state.get_valid_moves()
            tests.append(time.time() - start)
        print(sum(tests))

    def swap_turns(self) -> None:
        self.curr_turn, self.last_turn = self.last_turn, self.curr_turn
        self.get_valid_moves()

    def get_valid_moves(self) -> None:
        self.valid_moves.clear()
        for r, row in enumerate(self.arr):
            for c, piece in enumerate(row):
                if piece != 'empty' and piece.color == self.curr_turn:
                    self.valid_moves.update({(r, c): piece.get_moves(r, c)})
