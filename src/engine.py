from time import time
import random


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
        """self.board_array = [
            ['br', '--', '--', '--', 'bk', '--', '--', 'br'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', 'wp', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wr', '--', '--', '--', 'wk', '--', '--', 'wr']
        ]"""
        # create an 8x8 array to track changes to squares
        self.num_changes = [[0] * 8 for _ in range(8)]

        self.current_color = 'w'
        self.enemy_color = 'b'
        self.white_king_square = (7, 4)
        self.black_king_square = (0, 4)

        self.ep_square = ()

        self.move_generator = MoveGenerator(self)
        self.move_maker = MoveMaker(self)

        self.move_history = []
        self.valid_moves = self.move_generator.get_legal_moves()

    def is_checkmate(self):
        return len(self.valid_moves) == 0

    def get_pseudo_in_check(self):
        return [move.to_pos for move in self.move_generator.get_pseudo_legal_moves()]

    def get_legal_in_check(self):
        if hasattr(self, 'valid_moves'):
            return [move.to_pos for move in self.valid_moves]
        else:
            return []

    def swap_turns(self):
        self.current_color, self.enemy_color = self.enemy_color, self.current_color

    def get_movable_squares(self):
        return [move.from_pos for move in self.valid_moves]

    def get_moves_of_square(self, from_pos):
        return [move for move in self.valid_moves if move.from_pos == from_pos]

    def get_piece(self, row, col):
        return self.board_array[row][col]

    def edit_board_array(self, changes):
        """Takes an iterable of position-piece pairs and edits the board array by putting the pieces at the
        given positions. Also updates the king positions."""
        for pos, piece in changes:
            self.board_array[pos[0]][pos[1]] = piece

            # update king position
            if piece == 'wk':
                self.white_king_square = pos
            elif piece == 'bk':
                self.black_king_square = pos

    def count_changes(self, changes, is_undo):
        changed_squares = set(change[0] for change in changes)
        if is_undo:
            increment = -1
        else:
            increment = 1
        for r, c in changed_squares:
            self.num_changes[r][c] += increment


class MoveGenerator:
    def __init__(self, board_state):
        self.board_state = board_state
        self.board_array = board_state.board_array
        self.get_moves = {
            'p': self._generate_pawn_moves,
            'r': self._generate_by_direction,
            'k': self._generate_king_moves,
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

    def get_legal_moves(self) -> list:
        legal_moves = []
        for move in self.get_pseudo_legal_moves():

            self.board_state.move_maker.apply_move(move, swap_turns=True, regenerate_moves=False, count_changes=False)

            if self.board_state.current_color == 'w':
                king_pos = self.board_state.black_king_square
            else:
                king_pos = self.board_state.white_king_square

            if not king_pos in self.board_state.get_pseudo_in_check():
                legal_moves.append(move)

            self.board_state.move_maker.apply_move(is_undo=True, swap_turns=True, regenerate_moves=False, count_changes=False)

        return legal_moves

    def get_pseudo_legal_moves(self) -> list:
        color = self.board_state.current_color
        moves = []
        for r, row in enumerate(self.board_array):
            for c, square in enumerate(row):
                if square[0] == color:
                    piece_type = square[1]
                    moves.extend(self.get_moves[piece_type](r, c, self.args[piece_type]))

        return moves

    def _generate_pawn_moves(self, row, col, _):
        r_step = -1 if self.board_state.current_color == 'w' else 1
        next_row = row + r_step
        left_col = col - 1
        right_col = col + 1

        moves = []

        if 0 <= next_row <= 7:
            # forward movement
            if self.board_array[next_row][col] == '--':
                moves.append(PawnMove(self.board_state, (row, col), (next_row, col)))
                # check for double move
                if (row in (1, 6)) and  (0 <= next_row+r_step <= 7) and (self.board_array[next_row+r_step][col] == '--'):
                    moves.append(PawnMove(self.board_state, (row, col), (next_row+r_step, col), make_ep=True))

            # diagonal movement
            if left_col >= 0:
                if self.board_array[next_row][left_col][0] == self.board_state.enemy_color:
                    moves.append(PawnMove(self.board_state, (row, col), (next_row, left_col)))
                elif (next_row, left_col) == self.board_state.ep_square:
                    moves.append(PawnMove(self.board_state, (row, col), (next_row, left_col), is_ep=True))

            if right_col <= 7:
                if self.board_array[next_row][right_col][0] == self.board_state.enemy_color:
                    moves.append(PawnMove(self.board_state, (row, col), (next_row, right_col)))
                elif (next_row, right_col) == self.board_state.ep_square:
                    moves.append(PawnMove(self.board_state, (row, col), (next_row, right_col), is_ep=True))

        return moves

    def _generate_king_moves(self,row, col, possible):
        moves = []
        for r, c in ((row + r_step, col + c_step) for r_step, c_step in possible):
            if 0 <= r <= 7 and 0 <= c <= 7:
                piece = self.board_array[r][c]
                if piece == '--' or piece[0] == self.board_state.enemy_color:
                    moves.append(KingMove(self.board_state, from_pos=(row, col), to_pos=(r, c)))

        # check for castling moves
        if (row, col) not in (legal_in_check := self.board_state.get_legal_in_check()):
            # left castle
            if self.board_state.num_changes[row][0] == 0:
                l_castle = True
                for step in range(1, 4):
                    if self.board_array[row][col - step] != '--' or (row, col - step) in legal_in_check:
                        l_castle = False
                        break
                if l_castle:
                    moves.append(KingMove(self.board_state, from_pos=(row, col), to_pos=(row, col - 2), castle=True))

            # right castle
            if self.board_state.num_changes[row][7] == 0:
                r_castle = True
                for step in range(1, 3):
                    if self.board_array[row][col + step] != '--' or (row, col + step) in legal_in_check:
                        r_castle = False
                        break
                if r_castle:
                    moves.append(KingMove(self.board_state, from_pos=(row, col), to_pos=(row, col + 2), castle=True))

        return moves

    def _generate_by_possible(self, row, col, possible):
        moves = []
        for r, c in ((row + r_step, col + c_step) for r_step, c_step in possible):
            if 0 <= r <= 7 and 0 <= c <= 7:
                piece = self.board_array[r][c]
                if piece == '--' or piece[0] == self.board_state.enemy_color:
                    moves.append(Move(self.board_state, from_pos=(row, col), to_pos=(r, c)))

        return moves

    def _generate_by_direction(self, row, col, directions):
        moves = []
        for r_step, c_step in directions:
            r, c = row, col
            while 0 <= (r:=r+r_step) <= 7 and 0 <= (c:=c+c_step) <= 7:
                piece = self.board_array[r][c]
                if piece == '--':
                    moves.append(Move(self.board_state, from_pos=(row, col), to_pos=(r, c)))
                elif piece[0] == self.board_state.enemy_color:
                    moves.append(Move(self.board_state, from_pos=(row, col), to_pos=(r, c)))
                    break
                else:
                    break

        return moves


class MoveMaker:
    def __init__(self, board_state):
        self.board_state = board_state
        self.board_array = board_state.board_array

    def apply_move(self, move=None, is_undo=False, swap_turns=True, regenerate_moves=True, count_changes=True):
        if not is_undo:
            self._build_move(move)
            self.board_state.edit_board_array(move.changes)

            self.board_state.ep_square = move.new_ep_pos

            self.board_state.move_history.append(move)
        else:
            if move is None:
                try:
                    move = self.board_state.move_history.pop()
                except IndexError:
                    return -1  # make no changes

            self.board_state.edit_board_array(move.undo_changes)

            self.board_state.ep_square = move.old_ep_pos

        if count_changes:
            self.board_state.count_changes(move.changes, is_undo=is_undo)
        if swap_turns:
            self.board_state.swap_turns()
        if regenerate_moves:
            self.board_state.valid_moves = self.board_state.move_generator.get_legal_moves()

    def _build_move(self, move):
        moved_piece = self.board_state.get_piece(*move.from_pos)
        moved_color, moved_type = moved_piece[0], moved_piece[1]

        changes = []

        changes.extend([(move.from_pos, '--'), (move.to_pos, moved_piece)])

        if isinstance(move, PawnMove):
            ep_step = 1 if moved_color == 'w' else -1
            # pawn promotion
            if move.to_row in (0, 7):
                changes.append((move.to_pos, f"{moved_color}q"))
            elif move.make_ep:
                move.new_ep_pos = (move.to_row + ep_step, move.to_col)
            elif move.is_ep:
                changes.append(((move.to_row + ep_step, move.to_col), '--'))

        elif isinstance(move, KingMove):
            if move.castle:
                if move.to_col < 4:  # left castle
                    old_rook_pos = (move.to_row, 0)
                    new_rook_pos = (move.to_row, move.to_col + 1)
                    changes.extend([(new_rook_pos, f"{moved_color}r"), (old_rook_pos, '--')])
                else:  # right castle
                    old_rook_pos = (move.to_row, 7)
                    new_rook_pos = (move.to_row, move.to_col - 1)
                    changes.extend([(new_rook_pos, f"{moved_color}r"), (old_rook_pos, '--')])

        for change in changes:
            changed_position = change[0]
            move.changes.append(change)
            move.undo_changes.append((changed_position, self.board_state.get_piece(*changed_position)))


class Move:
    def __init__(self, board_state, from_pos, to_pos):
        self.board_state = board_state

        self.from_pos = from_pos
        self.to_pos = to_pos

        self.from_row, self.from_col = from_pos
        self.to_row, self.to_col = to_pos

        self.changes = []
        self.undo_changes = []

        self.new_ep_pos = ()
        self.old_ep_pos = self.board_state.ep_square

    def __eq__(self, other):
        return (self.from_pos, self.to_pos) == other

    def __repr__(self):
        return f"{self.from_pos} -> {self.to_pos}"


class PawnMove(Move):
    def __init__(self, board_state, from_pos, to_pos, make_ep=False, is_ep=False):
        Move.__init__(self, board_state, from_pos, to_pos)
        self.make_ep = make_ep
        self.is_ep = is_ep

class KingMove(Move):
    def __init__(self, board_state, from_pos, to_pos, castle=False):
        Move.__init__(self, board_state, from_pos, to_pos)
        self.castle = castle
