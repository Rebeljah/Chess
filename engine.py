from time import time


class BoardState:
    def __init__(self, app):
        self.app = app

        self.board_array = [
            ['br', 'bn', 'bb', 'bq', 'bk', 'bb', 'bn', 'br'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr']
        ]
        self.current_color = 'w'
        self.enemy_color = 'b'
        self.ep_pos = None
        self.valid_moves = {}

        self.move_generator = MoveGenerator(self)
        self.move_maker = MoveMaker(self)
        self.move_generator.generate_moves()

    def make_move(self, move):
        self.move_maker.make_move(move)
        self.swap_turns()
        self.move_generator.generate_moves()

    def undo_move(self, move=None, swap_tuns=False, regenerate_moves=False):
        """Undo the given move, or if none is given undo the last move taken"""
        self.move_maker.undo_move(move, swap_tuns, regenerate_moves)

    def swap_turns(self):
        self.current_color, self.enemy_color = self.enemy_color, self.current_color

    def get_from_positions(self):
        return self.valid_moves.keys()

    def get_moves_of_position(self, from_pos):
        return self.valid_moves.get(from_pos, [])


class MoveGenerator:
    def __init__(self, board_state):
        self.board_state = board_state
        self.board_array = board_state.board_array
        self.get_moves = {
            'p': self._generate_pawn_moves,
            'r': self._generate_by_direction,
            'k': self._generate_by_possible,
            'b': self._generate_by_direction,
            'q': self._generate_by_direction,
            'n': self._generate_by_possible
        }
        self.args = {
            'p': (),
            'r': ((-1, 0), (0, 1), (1, 0), (0, -1)),
            'b': ((-1, -1), (-1, 1), (1, 1), (1, -1)),
            'q': ((-1, -1), (-1, 1), (1, 1), (1, -1), (-1, 0), (0, 1), (1, 0), (0, -1)),
            'k': ((- 1, 0), (- 1, + 1), (0, + 1), (+ 1, + 1), (+ 1, 0), (+ 1, - 1), (0, - 1), (- 1, - 1)),
            'n': ((- 1, - 2), (+ 1, - 2), (- 2, - 1), (- 2, + 1), (- 1, + 2), (+ 1, + 2), (+ 2, + 1), (+ 2, - 1))
        }

    def generate_moves(self, color=None):
        """Get valid moves for one color or of one piece"""
        self.board_state.valid_moves = {}

        if color is None:  # default to color of current turn
            color = self.board_state.current_color

        for r, row in enumerate(self.board_array):
            for c, square in enumerate(row):
                if square[0] == color:
                    piece_type = square[1]
                    self.board_state.valid_moves[(r, c)] = self.get_moves[piece_type](r, c, self.args[piece_type])

    def _generate_pawn_moves(self, row, col, _):
        pawn_start_row = 6 if self.board_state.current_color == 'w' else 1
        r_step = -1 if self.board_state.current_color == 'w' else 1
        next_row = row + r_step
        left_col = col - 1
        right_col = col + 1

        moves = []

        if 0 <= next_row <= 7:
            # forward movement
            if self.board_array[next_row][col] == '--':
                moves.append(Move((row, col), (next_row, col)))
                # check for double move
                if row == pawn_start_row and self.board_array[next_row+r_step][col] == '--':
                    moves.append(Move((row, col), (next_row+r_step, col), creates_ep=True))

            # diagonal movement
            if left_col >= 0:
                if self.board_array[next_row][left_col][0] == self.board_state.enemy_color:
                    moves.append(Move((row, col), (next_row, left_col)))
                elif self.board_state.ep_pos == (next_row, left_col):
                    moves.append(Move((row, col), (next_row, left_col), is_ep=True))

            if right_col <= 7:
                if self.board_array[next_row][right_col][0] == self.board_state.enemy_color:
                    moves.append(Move((row, col), (next_row, right_col)))
                elif self.board_state.ep_pos == (next_row, right_col):
                    moves.append(Move((row, col), (next_row, right_col), is_ep=True))

        return moves

    def _generate_by_possible(self, row, col, possible):
        moves = []
        for r, c in ((row + r_change, col + c_change) for r_change, c_change in possible):
            if 0 <= r <= 7 and 0 <= c <= 7:
                piece = self.board_array[r][c]
            else:
                continue
            if piece == '--' or piece[0] == self.board_state.enemy_color:
                moves.append(Move(from_pos=(row, col), to_pos=(r, c)))

        return moves

    def _generate_by_direction(self, row, col, directions):
        moves = []
        for r_step, c_step in directions:
            r, c = row, col
            while 0 <= (r:=r+r_step) <= 7 and 0 <= (c:=c+c_step) <= 7:
                piece = self.board_array[r][c][0]
                if piece == '-':
                    moves.append(Move(from_pos=(row, col), to_pos=(r, c)))
                    continue
                elif piece == self.board_state.enemy_color:
                    moves.append(Move(from_pos=(row, col), to_pos=(r, c)))
                break

        return moves


class MoveMaker:
    def __init__(self, board_state):
        self.board_state = board_state
        self.board_array = board_state.board_array

        self.move_history = []

    def make_move(self, move):
        self.build_move(move)

        for pos, value in move.changes:
            self.board_array[pos[0]][pos[1]] = value

        self.board_state.ep_pos = move.new_ep_pos

        self.move_history.append(move)

    def undo_move(self, move, swap_tuns, regenerate_moves):
        if not move:
            try:
                move = self.move_history.pop()
            except IndexError:
                return -1

        for pos, value in move.undo_changes:
            self.board_array[pos[0]][pos[1]] = value

        self.board_state.ep_pos = move.old_ep_pos

        if swap_tuns:
            self.board_state.swap_turns()
        if regenerate_moves:
            self.board_state.move_generator.generate_moves()

    def build_move(self, move):
        def add_changes(move, changes):
            for change in changes:
                r, c = change[0]
                move.changes.append(change)
                move.undo_changes.append(((r, c), self.board_array[r][c]))

        from_r, from_c = move.from_pos
        to_r, to_c = move.to_pos

        moved_piece = self.board_array[from_r][from_c]
        moved_color, moved_type = moved_piece[0], moved_piece[1]

        move.old_ep_pos = self.board_state.ep_pos
        changes = [(move.from_pos, '--'), (move.to_pos, moved_piece)]

        if moved_piece[1] == 'p':
            ep_step = 1 if moved_color == 'w' else -1

            if to_r in (0, 7):
                changes.append((move.to_pos, f"{moved_color}q"))
            elif move.creates_ep:
                move.new_ep_pos = (to_r + ep_step, to_c)
            elif move.is_ep:
                changes.append(((to_r + ep_step, to_c), '--'))
            # pawn promotion to queen

        add_changes(move, changes)


class Move:
    def __init__(self, from_pos, to_pos, creates_ep=False, is_ep=False):
        self.from_pos = from_pos
        self.to_pos = to_pos

        self.creates_ep = creates_ep
        self.is_ep = is_ep

        self.changes = []
        self.new_ep_pos = None
        self.undo_changes = []
        self.old_ep_pos = None

    def __repr__(self):
        return f"{self.from_pos} -> {self.to_pos}"
