import board
import checkers_pieces
import copy
import gui

players = ["White", "Black"]
board_size = 10


def initialize_board(size):
    game_board = board.Board(size)
    for i in range(4):
        if i % 2 == 0:
            for j in range(game_board.size):
                if j % 2 != 0:
                    game_board.add_piece(i, j, checkers_pieces.Pawn("Black"))
        else:
            for j in range(game_board.size):
                if j % 2 == 0:
                    game_board.add_piece(i, j, checkers_pieces.Pawn("Black"))
    for i in range(1, 5):
        if i % 2 == 0:
            for j in range(game_board.size):
                if j % 2 != 0:
                    game_board.add_piece(-i, j, checkers_pieces.Pawn("White"))
        else:
            for j in range(game_board.size):
                if j % 2 == 0:
                    game_board.add_piece(-i, j, checkers_pieces.Pawn("White"))
    return game_board


class CapturePath:
    def __init__(self, i, j, board, active_player, directions=("ul", "ur", "ll", "lr"), leading_coords=(None, None)):
        self.saved_board = copy.deepcopy(board)
        self.coords = (i, j)
        self.upper_left = []
        self.upper_right = []
        self.lower_left = []
        self.lower_right = []
        self.leading_coords = leading_coords
        if board.tiles[i][j].promoted:
            self.build_queen_path(board, active_player, directions)
        else:
            self.build_path(board, active_player)
        self.prune_tree()

    def build_path(self, board, active_player):
        def evaluate_step(self, line, row, board, active_player, l_off, r_off):
            captured_coords = (line + l_off, row + r_off)
            self.saved_board.remove_piece(*captured_coords)
            self.saved_board.move_piece(line, row, line + 2 * l_off, row + 2 * r_off)
            step = CapturePath(line + 2 * l_off, row + 2 * r_off, self.saved_board, active_player, None, captured_coords)
            self.saved_board = copy.deepcopy(board)
            return step

        line, row = self.coords
        ul, ur, ll, lr = can_capture_from_position(line, row, self.saved_board, active_player)
        if ul:
            self.upper_left.append(evaluate_step(self, line, row, board, active_player, -1, -1))
        if ur:
            self.upper_right.append(evaluate_step(self, line, row, board, active_player, -1, +1))
        if ll:
            self.lower_left.append(evaluate_step(self, line, row, board, active_player, +1, -1))
        if lr:
            self.lower_right.append(evaluate_step(self, line, row, board, active_player, +1, +1))

    def build_queen_path(self, board, active_player, directions):
        def evaluate_step(self, line, row, ul_lr, board, active_player, directions, l_off, r_off, node):
            test_line = ul_lr[1][0]
            test_row = ul_lr[1][1]
            captured_coords = (test_line - l_off, test_row - r_off)
            self.saved_board.remove_piece(*captured_coords)
            self.saved_board.move_piece(line, row, test_line, test_row)
            node.append(CapturePath(test_line, test_row, self.saved_board, active_player, directions, captured_coords))
            line = test_line
            row = test_row
            test_row += r_off
            test_line += l_off
            while not (piece_exists(test_line, test_row, self.saved_board)):
                self.saved_board.move_piece(line, row, test_line, test_row)
                node.append(CapturePath(test_line, test_row, self.saved_board, active_player, directions, captured_coords))
                line = test_line
                row = test_row
                test_row += r_off
                test_line += l_off
            self.saved_board = copy.deepcopy(board)

        line, row = self.coords
        ul, ur, ll, lr, = queen_can_capture_from_position(line, row, self.saved_board, active_player)
        if ul[0] and "ul" in directions:
            evaluate_step(self, line, row, ul, board, active_player, ["ul", "ur", "ll"], -1, -1, self.upper_left)
        if ur[0] and "ur" in directions:
            evaluate_step(self, line, row, ur, board, active_player, ["ul", "ur", "lr"], -1, +1, self.upper_right)
        if ll[0] and "ll" in directions:
            evaluate_step(self, line, row, ll, board, active_player, ["ul", "lr", "ll"], +1, -1, self.lower_left)
        if lr[0] and "lr" in directions:
            evaluate_step(self, line, row, lr, board, active_player, ["ur", "lr", "ll"], +1, +1, self.lower_right)

    def depth(self):
        ul_depth = max([x.depth() for x in self.upper_left]) if self.upper_left else 0
        ur_depth = max([x.depth() for x in self.upper_right]) if self.upper_right else 0
        ll_depth = max([x.depth() for x in self.lower_left]) if self.lower_left else 0
        lr_depth = max([x.depth() for x in self.lower_right]) if self.lower_right else 0
        return max(ul_depth, ur_depth, ll_depth, lr_depth) + 1

    def prune_tree(self):
        max_depth = self.depth()
        branches = [self.upper_left, self.upper_right, self.lower_left, self.lower_right]
        for branch in branches:
            i = 0
            while i < len(branch):
                node = branch[i]
                if node.depth() < max_depth - 1:
                    del(branch[i])
                else:
                    i += 1


def piece_exists(line, row, board):
    size = board.size
    if 0 <= line < size and 0 <= row < size:
        if board.tiles[line][row]:
            return board.tiles[line][row]
        else:
            return False
    else:
        return True  # All tiles outside of the board are considered as occupied to prevent movement


def pawn_to_promote(end_line, piece):
    if end_line == 0 or end_line == board_size - 1:
        if not piece.promoted:
            piece.promote()


def can_capture_from_position(line, row, board, active_player):
    def can_capture(target_line, target_row, board):
        piece = piece_exists(line, row, board)
        piece_to_capture = piece_exists(target_line, target_row, board)
        empty_destination = not (piece_exists(target_line-(line-target_line), target_row-(row-target_row), board))
        return (
                piece.owner is active_player and
                piece_to_capture and
                empty_destination and
                piece_to_capture.owner is not active_player
                )

    upper_left = can_capture(line-1, row-1, board)
    upper_right = can_capture(line-1, row+1, board)
    lower_left = can_capture(line+1, row-1, board)
    lower_right = can_capture(line+1, row+1, board)
    return upper_left, upper_right, lower_left, lower_right


def queen_can_capture_from_position(line, row, board, active_player, directions=("ul", "ur", "ll", "lr")):
    def test_diagonal(line, row, board, active_player, l_off, r_off):
        piece = piece_exists(line, row, board)
        while 0 <= line + l_off < board.size and 0 <= row + r_off < board.size:
            if not(piece_exists(line + l_off, row + r_off, board)):
                line += l_off
                row += r_off
            else:
                pot_capture = piece_exists(line + l_off, row + r_off, board)
                if (pot_capture.owner is not active_player and
                        not(piece_exists(line + 2*l_off, row + 2*r_off, board)) and
                        piece.owner is active_player):
                    return True, (line + 2*l_off, row + 2*r_off)
                else:
                    return False, None
        return False, None

    upper_left = test_diagonal(line, row, board, active_player, -1, -1) if "ul" in directions else (False, None)
    upper_right = test_diagonal(line, row, board, active_player, -1, +1) if "ur" in directions else (False, None)
    lower_left = test_diagonal(line, row, board, active_player, +1, -1) if "ll" in directions else (False, None)
    lower_right = test_diagonal(line, row, board, active_player, +1, +1) if "lr" in directions else (False, None)
    return upper_left, upper_right, lower_left, lower_right


def pawn_move_legal(start_line, start_row, end_line, end_row, piece, board, active_player):
    """returns True if the considered move is legal"""
    if active_player == piece.owner and not piece_exists(end_line, end_row, board):
        if piece.type == "Black_pawn":
            direction = -1
        else:
            direction = 1
        return (start_line == end_line + direction) and ((start_row == end_row + 1) or (start_row == end_row - 1))


def queen_move_legal(start_line, start_row, end_line, end_row, piece, board, active_player):
    """returns True if the considered move is legal"""
    def test_diagonal(line, row, board, l_off, r_off, pot_moves):
        while 0 <= line + l_off < board.size and 0 <= row + r_off < board.size:
            if not(piece_exists(line + l_off, row + r_off, board)):
                line += l_off
                row += r_off
                pot_moves.add((line, row))
            else:
                return

    potential_destinations = set()
    if active_player == piece.owner and not piece_exists(end_line, end_row, board):
        test_diagonal(start_line, start_row, board, -1, -1, potential_destinations)
        test_diagonal(start_line, start_row, board, +1, -1, potential_destinations)
        test_diagonal(start_line, start_row, board, -1, +1, potential_destinations)
        test_diagonal(start_line, start_row, board, +1, +1, potential_destinations)
        if (end_line, end_row) in potential_destinations:
            return True
    return False


def find_all_possible_captures(board, active_player):
    """Returns the tree roots of all legal captures for this turn"""
    path_starts = []
    max_captures = 2 # no capture is depth 1, so save only capture from depth 2
    for i, line in enumerate(board.tiles):
        for j, tile in enumerate(line):
            if tile:
                pot_path = CapturePath(i, j, board, active_player)
                pot_max_capt = pot_path.depth()
                if pot_max_capt > max_captures:
                    path_starts = [pot_path]
                    max_captures = pot_max_capt
                elif pot_max_capt == max_captures:
                    path_starts.append(pot_path)
    return path_starts


def take_legal(capt_node, end_line, end_row):
    branches = [capt_node.upper_left, capt_node.upper_right, capt_node.lower_left, capt_node.lower_right]
    for branch in branches:
        for pot_destination in branch:
            if pot_destination.coords == (end_line, end_row):
                return True, pot_destination
    return False, None


def execute_move(start_line, start_row, end_line, end_row, board, active_player):
    """move the piece if the movement considered is legal"""
    piece = piece_exists(start_line, start_row, board)
    if piece:
        if ((not piece.promoted
                and pawn_move_legal(start_line, start_row, end_line, end_row, piece, board, active_player)) or
                (piece.promoted
                    and queen_move_legal(start_line, start_row, end_line, end_row, piece, board, active_player))):
            board.move_piece(start_line, start_row, end_line, end_row)
            return True
    return False


def execute_take(end_line, end_row, board, capt_node):
    """move the piece and remove the enemy piece if the take is legal, return the next step of the captures
     if the move is legal, else return false"""
    start_line, start_row = capt_node.coords
    legal, destination_node = take_legal(capt_node, end_line, end_row)
    if legal:
        board.move_piece(start_line, start_row, end_line, end_row)
        board.remove_piece(*destination_node.leading_coords)
        return destination_node
    else:
        return False


class Turn:
    def __init__(self, active_player, board):
        self.player = active_player
        self.roots = find_all_possible_captures(board, self.player)

    def play_turn(self, start_line, start_row, end_line, end_row, board):
        if self.roots:
            for root in self.roots:
                if (start_line, start_row) == root.coords:
                    destination_node = execute_take(end_line, end_row, board, root)
                    if destination_node:
                        self.roots = [destination_node]
                        branches = [destination_node.upper_left,
                                    destination_node.upper_right,
                                    destination_node.lower_left,
                                    destination_node.lower_right]
                        if not any(branches):
                            return True

        else:
            moved = execute_move(start_line, start_row, end_line, end_row, board, self.player)
            return moved