
class Engine:
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

    def get_endgame_state(self):
        checkmate = False
        stalemate = False

        if len(self.valid_moves) == 0:
            # check if the king is in check
            if self.current_color == 'w':
                king_pos = self.white_king_square
            else:
                king_pos = self.black_king_square

            self.swap_turns()
            if king_pos in self.get_pseudo_in_check():
                checkmate = True
            else:
                stalemate = True
            self.swap_turns()

        return stalemate, checkmate

    def get_pseudo_in_check(self) -> list:
        """
        Search for pseudo-legal moves and return square positions that are in check

        :return: list: A list of squares in pseudo-legal check
        """
        return [move.to_pos for move in self.move_generator.get_pseudo_legal_moves()]

    def get_legal_in_check(self) -> list:
        """
        Get a list of the positions that are currently in legal check

        :return: list: squares that are legally checked by enemy pieces
        """

        if hasattr(self, 'valid_moves'):
            return [move.to_pos for move in self.valid_moves]
        else:
            return []

    def get_movable_squares(self):
        """
        Get the starting positions of each from from the list of valid moves

        :return: list: the starting positions of valid moves
        """

        return [move.from_pos for move in self.valid_moves]

    def get_moves_of_square(self, from_pos) -> list:
        """
        Return all of the valid moves that start from the given position

        :param from_pos: tuple: the row, column location of the target square
        :return: list: moves that start from the given position
        """

        return [move for move in self.valid_moves if move.from_pos == from_pos]

    def swap_turns(self) -> None:
        """Swap the current color and the enemy color"""

        self.current_color, self.enemy_color = self.enemy_color, self.current_color

    def get_piece(self, row, col) -> str:
        """
        Returns the string that represents the pieces at the given row, and column

        :param row: the row of the piece
        :param col: the column of the piece
        :return: string representation of  the piece from the board array
        """

        return self.board_array[row][col]

    def edit_board_array(self, changes) -> None:
        """
        Edit the board array and update positions of king pieces

        Takes in a list or tuple of changes and applies each change to the board array

        :param changes: an array of [pos, piece] pairs (position is a row, column pair)
        :return: None
        """

        for pos, piece in changes:
            self.board_array[pos[0]][pos[1]] = piece

            # update king position
            if piece == 'wk':
                self.white_king_square = pos
            elif piece == 'bk':
                self.black_king_square = pos

    def count_changes(self, changes, is_undo) -> None:
        """
        Updates the count of changes to squares that are changed by a set of changes

        The method will extract the location from each change and consolidate them into a set that contains all of
        the squares that were changed. For each position, the number of changes is either incremented or decremented
        depending on whether the move is being made or undone.

        :param changes: an array of [pos, piece] pairs (position is a row, column pair)
        :param is_undo: bool:
        :return: None
        """
        changed_squares = set(change[0] for change in changes)
        if is_undo:
            increment = -1
        else:
            increment = 1
        for r, c in changed_squares:
            self.num_changes[r][c] += increment


class MoveGenerator:
    def __init__(self, engine):
        self.engine = engine
        self.board_array = engine.board_array
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
        """
        Filter out illegal move by applying each pseudo-legal move and checking if the move results in a checked king.

        First, pseudo-legal moves are generated, then for each pseudo-legal move, the move is applied to the board array.
        Then, the pseudo-legal moves are regenerated from the enemy perspective. If this results in the friendly king
        being in check, the move is not added.

        :return: list: a list of moves that don't result in the king being in check
        """

        legal_moves = []
        for move in self.get_pseudo_legal_moves():

            self.engine.move_maker.apply_move(move, swap_turns=True, regenerate_moves=False, count_changes=False)

            if self.engine.current_color == 'w':
                king_pos = self.engine.black_king_square
            else:
                king_pos = self.engine.white_king_square

            if king_pos not in self.engine.get_pseudo_in_check():
                legal_moves.append(move)

            self.engine.move_maker.apply_move(is_undo=True, swap_turns=True, regenerate_moves=False, count_changes=False)

        return legal_moves

    def get_pseudo_legal_moves(self) -> list:
        """
        Get a list of pseudo-legal moves without checking whether or not the moves place the enemy king in check

        :return: list: all moves, whether or not they place the king in check
        """

        color = self.engine.current_color
        moves = []
        for r, row in enumerate(self.board_array):
            for c, square in enumerate(row):
                if square[0] == color:
                    piece_type = square[1]
                    moves.extend(self.get_moves[piece_type](r, c, self.args[piece_type]))

        return moves

    def _generate_pawn_moves(self, row, col, _):
        r_step = -1 if self.engine.current_color == 'w' else 1
        next_row = row + r_step
        left_col = col - 1
        right_col = col + 1

        moves = []

        if 0 <= next_row <= 7:
            # forward movement
            if self.board_array[next_row][col] == '--':
                moves.append(PawnMove(self.engine, (row, col), (next_row, col)))
                # check for double move
                if (row in (1, 6)) and  (0 <= next_row+r_step <= 7) and (self.board_array[next_row+r_step][col] == '--'):
                    moves.append(PawnMove(self.engine, (row, col), (next_row + r_step, col), make_ep=True))

            # diagonal movement
            if left_col >= 0:
                if self.board_array[next_row][left_col][0] == self.engine.enemy_color:
                    moves.append(PawnMove(self.engine, (row, col), (next_row, left_col)))
                elif (next_row, left_col) == self.engine.ep_square:
                    moves.append(PawnMove(self.engine, (row, col), (next_row, left_col), is_ep=True))

            if right_col <= 7:
                if self.board_array[next_row][right_col][0] == self.engine.enemy_color:
                    moves.append(PawnMove(self.engine, (row, col), (next_row, right_col)))
                elif (next_row, right_col) == self.engine.ep_square:
                    moves.append(PawnMove(self.engine, (row, col), (next_row, right_col), is_ep=True))

        return moves

    def _generate_king_moves(self,row, col, possible):
        moves = []
        for r, c in ((row + r_step, col + c_step) for r_step, c_step in possible):
            if 0 <= r <= 7 and 0 <= c <= 7:
                piece = self.board_array[r][c]
                if piece == '--' or piece[0] == self.engine.enemy_color:
                    moves.append(KingMove(self.engine, from_pos=(row, col), to_pos=(r, c)))

        # check for castling moves
        if (row, col) not in (legal_in_check := self.engine.get_legal_in_check()):
            # left castle
            if self.engine.num_changes[row][0] == 0:
                l_castle = True
                for step in range(1, 4):
                    if self.board_array[row][col - step] != '--' or (row, col - step) in legal_in_check:
                        l_castle = False
                        break
                if l_castle:
                    moves.append(KingMove(self.engine, from_pos=(row, col), to_pos=(row, col - 2), castle=True))

            # right castle
            if self.engine.num_changes[row][7] == 0:
                r_castle = True
                for step in range(1, 3):
                    if self.board_array[row][col + step] != '--' or (row, col + step) in legal_in_check:
                        r_castle = False
                        break
                if r_castle:
                    moves.append(KingMove(self.engine, from_pos=(row, col), to_pos=(row, col + 2), castle=True))

        return moves

    def _generate_by_possible(self, row, col, possible):
        moves = []
        for r, c in ((row + r_step, col + c_step) for r_step, c_step in possible):
            if 0 <= r <= 7 and 0 <= c <= 7:
                piece = self.board_array[r][c]
                if piece == '--' or piece[0] == self.engine.enemy_color:
                    moves.append(Move(self.engine, from_pos=(row, col), to_pos=(r, c)))

        return moves

    def _generate_by_direction(self, row, col, directions):
        moves = []
        for r_step, c_step in directions:
            r, c = row, col
            while 0 <= (r:=r+r_step) <= 7 and 0 <= (c:=c+c_step) <= 7:
                piece = self.board_array[r][c]
                if piece == '--':
                    moves.append(Move(self.engine, from_pos=(row, col), to_pos=(r, c)))
                elif piece[0] == self.engine.enemy_color:
                    moves.append(Move(self.engine, from_pos=(row, col), to_pos=(r, c)))
                    break
                else:
                    break

        return moves


class MoveMaker:
    def __init__(self, engine):
        self.engine = engine
        self.board_array = engine.board_array

    def apply_move(self, move=None, is_undo=False, swap_turns=True, regenerate_moves=True, count_changes=True) -> None:
        """
        Make or undo the changes of a move.

        If making a move, build the changes of the move and then apply those changes to the board array. When rolling
        back a move, if no move is provided, the last move is popped from the move history.

        :param move: the move object to be made or undone
        :param is_undo: whether or not to make or undo the move
        :param swap_turns: whether or not to swap the current color after changes are made
        :param regenerate_moves: whether or not to regenerate legal moves after the move is made
        :param count_changes: whether or not to record the changes
        :return: None
        """

        if not is_undo:
            self._build_move(move)
            self.engine.edit_board_array(move.changes)
            self.engine.ep_square = move.new_ep_pos
            self.engine.move_history.append(move)
        else:
            if move is None:
                try:
                    move = self.engine.move_history.pop()
                except IndexError:
                    return -1  # make no changes

            self.engine.edit_board_array(move.undo_changes)
            self.engine.ep_square = move.old_ep_pos

        if count_changes:
            self.engine.count_changes(move.changes, is_undo=is_undo)
        if swap_turns:
            self.engine.swap_turns()
        if regenerate_moves:
            self.engine.valid_moves = self.engine.move_generator.get_legal_moves()

    def _build_move(self, move) -> None:
        """
        Add changes to the given move.

        :param move: The move object to build
        :return: None
        """

        moved_piece = self.engine.get_piece(*move.from_pos)
        moved_color, moved_type = moved_piece[0], moved_piece[1]

        changes = [(move.from_pos, '--'), (move.to_pos, moved_piece)]

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
            move.undo_changes.append((changed_position, self.engine.get_piece(*changed_position)))


class Move:
    def __init__(self, engine, from_pos, to_pos):
        self.board_state = engine

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
    def __init__(self, engine, from_pos, to_pos, make_ep=False, is_ep=False):
        Move.__init__(self, engine, from_pos, to_pos)
        self.make_ep = make_ep
        self.is_ep = is_ep


class KingMove(Move):
    def __init__(self, engine, from_pos, to_pos, castle=False):
        Move.__init__(self, engine, from_pos, to_pos)
        self.castle = castle
