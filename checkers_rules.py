import board
import checkers_pieces
import copy
from abstract_rules import AbstractTurn
players = ["White", "Black"]
board_size = 10


def initialize_board(size):
    game_board = board.Board(size)
    for i in range(4):
        if i % 2 == 0:
            for j in range(game_board.size):
                if j % 2 != 0:
                    game_board.add_piece(i, j, checkers_pieces.Pawn(players[1]))
        else:
            for j in range(game_board.size):
                if j % 2 == 0:
                    game_board.add_piece(i, j, checkers_pieces.Pawn(players[1]))
    for i in range(1, 5):
        if i % 2 == 0:
            for j in range(game_board.size):
                if j % 2 != 0:
                    game_board.add_piece(-i, j, checkers_pieces.Pawn(players[0]))
        else:
            for j in range(game_board.size):
                if j % 2 == 0:
                    game_board.add_piece(-i, j, checkers_pieces.Pawn(players[0]))
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
            evaluate_step(self, line, row, ul, board, active_player, ("ul", "ur", "ll"), -1, -1, self.upper_left)
        if ur[0] and "ur" in directions:
            evaluate_step(self, line, row, ur, board, active_player, ("ul", "ur", "lr"), -1, +1, self.upper_right)
        if ll[0] and "ll" in directions:
            evaluate_step(self, line, row, ll, board, active_player, ("ul", "lr", "ll"), +1, -1, self.lower_left)
        if lr[0] and "lr" in directions:
            evaluate_step(self, line, row, lr, board, active_player, ("ur", "lr", "ll"), +1, +1, self.lower_right)

    def depth(self):
        ul_depth = max([x.depth() for x in self.upper_left]) if self.upper_left else 0
        ur_depth = max([x.depth() for x in self.upper_right]) if self.upper_right else 0
        ll_depth = max([x.depth() for x in self.lower_left]) if self.lower_left else 0
        lr_depth = max([x.depth() for x in self.lower_right]) if self.lower_right else 0
        return max(ul_depth, ur_depth, ll_depth, lr_depth) + 1

    def prune_tree(self):  # necessary to keep only the paths leading to the most captures
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
    """Check if a piece exists in the tile, if a piece exists returns the piece, if not return False.
    If the coordinates are outside of the board returns True to block all moves outside of the board."""
    size = board.size
    if 0 <= line < size and 0 <= row < size:
        if board.tiles[line][row]:
            return board.tiles[line][row]
        else:
            return False
    else:
        return True  # All tiles outside of the board are considered as occupied to prevent movement


def pawn_to_promote(end_line, piece):
    if (end_line == 0 and piece.owner == players[0]) or (end_line == board_size - 1 and piece.owner == players[1]):
        if not piece.promoted:
            piece.promote()


def can_capture_from_position(line, row, board, active_player):
    """Returns 4 truthy values for whether a pawn can capture in the 4 diagonals
    respectively upper left, upper right, lower left, lower right"""
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
    """Returns 4 truthy values and the coordinates of the closest destination tiles for wether a queen
     can capture in the 4 diagonals respectively upper left, upper right, lower left, lower right"""
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
    """Returns True if the considered move is legal"""
    if active_player == piece.owner and not piece_exists(end_line, end_row, board):
        if piece.type == "{}_pawn".format(players[1]):
            direction = -1
        else:
            direction = 1
        return (start_line == end_line + direction) and ((start_row == end_row + 1) or (start_row == end_row - 1))


def find_all_queen_moves(start_line, start_row, piece, board, active_player):
    """Returns a set containing all the tiles available as queen destination"""
    def test_diagonal(line, row, board, l_off, r_off, pot_moves):
        while 0 <= line + l_off < board.size and 0 <= row + r_off < board.size:
            if not(piece_exists(line + l_off, row + r_off, board)):
                line += l_off
                row += r_off
                pot_moves.add((line, row))
            else:
                return

    potential_destinations = set()
    if active_player == piece.owner:
        test_diagonal(start_line, start_row, board, -1, -1, potential_destinations)
        test_diagonal(start_line, start_row, board, +1, -1, potential_destinations)
        test_diagonal(start_line, start_row, board, -1, +1, potential_destinations)
        test_diagonal(start_line, start_row, board, +1, +1, potential_destinations)
    return potential_destinations


def queen_move_legal(start_line, start_row, end_line, end_row, piece, board, active_player):
    """Returns True if the considered move is legal"""
    if piece_exists(end_line, end_row, board):
        return False
    potential_destinations = find_all_queen_moves(start_line, start_row, piece, board, active_player)
    if (end_line, end_row) in potential_destinations:
        return True
    else:
        return False


def find_all_possible_captures(board, active_player):
    """Returns the tree roots of all legal captures for this turn, return empty list if no captures possible"""
    path_starts = []
    max_captures = 2  # no capture is depth 1, so save only capture from depth 2
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


def find_all_possible_moves(board, active_player):
    """Returns a list of tuples (start tile, end tile) for each possible move for the active player"""
    pot_moves = []
    for line in range(board.size):
        for row in range(board.size):
            piece = piece_exists(line, row, board)
            if piece:
                if not piece.promoted:
                    dir_tested = -1 if active_player == players[0] else 1
                    if pawn_move_legal(line, row, line + dir_tested, row + 1, piece, board, active_player):
                        pot_moves.append(((line, row), (line + dir_tested, row + 1)))
                    if pawn_move_legal(line, row, line + dir_tested, row - 1, piece, board, active_player):
                        pot_moves.append(((line, row), (line + dir_tested, row - 1)))
                else:
                    queen_dest = find_all_queen_moves(line, row, piece, board, active_player)
                    pot_moves.extend(zip([(line, row)]*len(queen_dest), queen_dest))
    return pot_moves


def take_legal(capt_node, end_line, end_row):
    """Returns True and the destination tile if the attempted capture is legal, else Returns False, None"""
    branches = [capt_node.upper_left, capt_node.upper_right, capt_node.lower_left, capt_node.lower_right]
    for branch in branches:
        for pot_destination in branch:
            if pot_destination.coords == (end_line, end_row):
                return True, pot_destination
    return False, None


def execute_move(start_line, start_row, end_line, end_row, board, piece, active_player):
    """Moves the piece if the movement considered is legal"""
    if piece:
        if ((not piece.promoted
                and pawn_move_legal(start_line, start_row, end_line, end_row, piece, board, active_player)) or
                (piece.promoted
                    and queen_move_legal(start_line, start_row, end_line, end_row, piece, board, active_player))):
            board.move_piece(start_line, start_row, end_line, end_row)
            return True
    return False


def execute_take(end_line, end_row, board, capt_node):
    """Moves the piece and removes the enemy piece if the take is legal.
     Returns the next step of the captures if the move is legal, else returns false"""
    start_line, start_row = capt_node.coords
    legal, destination_node = take_legal(capt_node, end_line, end_row)
    if legal:
        board.move_piece(start_line, start_row, end_line, end_row)
        board.remove_piece(*destination_node.leading_coords)
        return destination_node
    else:
        return False


def game_over(board, active_player):
    """Tests the game over conditions return True and the winning player if one condition is met"""
    piece_counts = dict(zip(players, [0, 0]))
    for line in range(board_size):
        for row in range(board_size):
            piece = piece_exists(line, row, board)
            if piece:
                piece_counts[piece.owner] += 1
    for player, pieces in piece_counts.items():
        if pieces == 0:  # if a player has no more pieces they lose the game
            winner = [x for x in players if x is not active_player]
            return True, winner[0]

    pot_moves = find_all_possible_moves(board, active_player)
    pot_capt = find_all_possible_captures(board, active_player)
    if not pot_moves and not pot_capt:  # if a player cannot move they lose the game
        winner = [x for x in players if x is not active_player]
        return True, winner[0]

    return False, None


class Turn(AbstractTurn):
    def __init__(self, active_player, board):
        super().__init__()
        self.player = active_player
        self.roots = find_all_possible_captures(board, self.player)

    def play_turn(self, start_line, start_row, end_line, end_row, board):
        """Tries to execute the move given as input. Returns True if the move was executed,
        or False if the move was impossible"""
        piece = piece_exists(start_line, start_row, board)
        if piece:
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
                                pawn_to_promote(end_line, piece)
                                return True
                            else:
                                return False

            else:
                moved = execute_move(start_line, start_row, end_line, end_row, board, piece, self.player)
                if moved:
                    pawn_to_promote(end_line, piece)
                return moved
