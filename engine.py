class BoardState:
    def __init__(self):
        self.arr = [
            ['br', 'bn', 'bb', 'bq', 'bk', 'bb', 'bn', 'br'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr']
        ]
        self.max_index = len(self.arr) - 1
        self.curr_turn = 'w'
        self.last_turn = 'b'
        self.valid_moves = {}
        self.get_valid_moves()

    def swap_turns(self):
        self.curr_turn, self.last_turn = self.last_turn, self.curr_turn
        self.get_valid_moves()

    def get_valid_moves(self) -> None:
        self.valid_moves.clear()
        get_moves = {
            'p': self.get_pawn_moves, 'r': self.get_rook_moves, 'k': self.get_king_moves,
            'b': self.get_bishop_moves, 'q': self.get_queen_moves, 'n': self.get_knight_moves
        }
        for r, row in enumerate(self.arr):
            for c, square in enumerate(row):
                if square[0] == self.curr_turn:
                    self.valid_moves.update({(r, c): get_moves[square[1]](r, c)})

    def get_pawn_moves(self, row, col):
        moves = []
        step = -1 if self.curr_turn == 'w' else 1
        start_row = 6 if self.curr_turn == 'w' else 1
        r = row + step
        if 0 <= r <= self.max_index:
            # forward movement
            if self.arr[r][col] == '--':
                moves.append((r, col))
                if row == start_row and self.arr[r + step][col] == '--':
                    moves.append((r + step, col))
            # diagonal movement
            if (c := col - 1) >= 0:
                if self.arr[r][c][0] == self.last_turn:
                    moves.append((r, c))
            if (c := col + 1) <= self.max_index:
                if self.arr[r][c][0] == self.last_turn:
                    moves.append((r, c))
        return moves

    def get_knight_moves(self, r , c):
        moves = []
        possible = [(r-1, c-2), (r+1, c-2), (r-2, c-1), (r-2, c+1), (r-1, c+2), (r+1, c+2), (r+2, c+1), (r+2, c-1)]
        for r, c in possible:
            if (0 <= r <= self.max_index) and (0 <= c <= self.max_index) and (self.arr[r][c][0] != self.curr_turn):
                moves.append((r, c))
        return moves

    def get_king_moves(self, row, col):
        moves = []
        r, c = row, col
        possible = [(r - 1, c), (r - 1, c + 1), (r, c + 1), (r + 1, c + 1), (r + 1, c), (r + 1, c - 1), (r, c - 1),
                    (r - 1, c - 1)]
        for r, c in possible:
            if (0 <= r <= self.max_index) and (0 <= c <= self.max_index) and self.arr[r][c][
                0] != self.curr_turn:
                moves.append((r, c))
        return moves

    def get_rook_moves(self, row, col):
        moves = []
        for r_step, c_step in ((-1, 0), (0, 1), (1, 0), (0, -1)):
            r, c = row, col
            while (0 <= (r := r+r_step) <= self.max_index) and (0 <= (c := c+c_step) <= self.max_index):
                if (square := self.arr[r][c]) == '--':
                    moves.append((r, c))
                elif square[0] == self.last_turn:
                    moves.append((r, c))
                    break
                else:
                    break
        return moves

    def get_bishop_moves(self, row, col):
        moves = []
        for r_step, c_step in ((-1, -1), (-1, 1), (1, 1), (1, -1)):
            r, c = row, col
            while (0 <= (c := c+c_step) <= self.max_index) and (0 <= (r := r+r_step) <= self.max_index):
                if (square := self.arr[r][c]) == '--':
                    moves.append((r, c))
                elif square[0] != self.curr_turn:
                    moves.append((r, c))
                    break
                else:
                    break
        return moves

    def get_queen_moves(self, row ,col):
        return self.get_bishop_moves(row, col) + self.get_rook_moves(row, col)