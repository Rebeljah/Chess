class BoardState:
    def __init__(self):
        self.board = [
            ['br', 'bn', 'bb', 'bq', 'bk', 'bb', 'bn', 'br'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr']
        ]
        self.color_curr_turn = 'w'
        self.color_last_turn = 'b'
        self.valid_moves: list = self.get_valid_moves()
    
    def get_valid_moves(self):
        valid_moves = {}
        for row in range(8):
            for col in range(8):
                if (name := self.board[row][col])[0] == self.color_curr_turn:
                    if name[1] == 'p':
                        valid_moves.update({(row, col): self.get_pawn_moves(row, col)})
                    elif name[1] == 'r':
                        valid_moves.update({(row, col): self.get_rook_moves(row, col)})
        print(valid_moves)
    
    def get_pawn_moves(self, row, col):
        moves = []
        step = -1 if self.color_curr_turn == 'w' else 1
        start_row = 6 if self.color_curr_turn == 'w' else 1
        next_row = row + step
        if 0 <= next_row <= len(self.board) - 1:
            # forward movement
            if self.board[next_row][col] == '--':
                moves.append((next_row, col))
                if row == start_row and self.board[next_row + step][col] == '--':
                    moves.append((next_row + step, col))
            # diagonal movement
            if (next_col := col - 1) >= 0:
                if self.board[next_row][next_col][0] == self.color_last_turn:
                    moves.append((next_row, next_col))
            if (next_col := col + 1) < len(self.board) - 1:
                if self.board[next_row][next_col][0] == self.color_last_turn:
                    moves.append((next_row, next_col))
        return moves
    
    def get_rook_moves(self, row, col):
        return None