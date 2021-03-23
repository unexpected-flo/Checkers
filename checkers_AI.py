import checkers_rules as rules
from copy import deepcopy
from random import randint


class AI:
    def __init__(self, ia_color, adv_color):
        self.color = ia_color
        self.adversary_color = adv_color
        self.current_take = None

    def score_position(self, board):
        piece_counts = dict(zip(rules.players, [0, 0]))
        for line in range(rules.board_size):
            for row in range(rules.board_size):
                piece = rules.piece_exists(line, row, board)
                if piece:
                    piece_counts[piece.owner] += 1

        score = piece_counts[self.color] - piece_counts[self.adversary_color]
        return score

    @staticmethod
    def potential_moves(board, active_player):
        pot_moves = []
        pot_takes = rules.find_all_possible_captures(board, active_player)

        if not pot_takes:
            pot_moves = rules.find_all_possible_moves(board, active_player)

        return pot_moves, pot_takes


class RandomAI(AI):
    def play(self, board):
        if not self.current_take:
            pot_moves, pot_takes = self.potential_moves(board, self.color)
        else:
            node = self.current_take
            destinations = [node.upper_left, node.upper_right, node.lower_left, node.lower_right]
            if not (any(destinations)):
                self.current_take = []
                pot_moves, pot_takes = self.potential_moves(board, self.color)
            else:
                pot_moves = []
                pot_takes = self.current_take

        if pot_moves:
            guess = randint(0, len(pot_moves)-1)
            (sl, sr), (el, er) = pot_moves[guess]
            return sl, sr, el, er
        if pot_takes:
            guess = randint(0, len(pot_takes)-1)
            node = pot_takes[guess]
            pot_dest = []
            destinations = [node.upper_left, node.upper_right, node.lower_left, node.lower_right]
            for branch in destinations:
                for dest in branch:
                    if dest:
                        pot_dest.append(dest)
            dest_guess = randint(0, len(pot_dest)-1)
            dest = pot_dest[dest_guess]
            sl, sr = node.coords
            el, er = dest.coords
            return sl, sr, el, er


class MinmaxAI(AI):
    def __init__(self, ia_color, adv_color, depth=2):
        super().__init__(ia_color, adv_color)
        self.depth = depth

    def find_boards_after_take(self, board, take_root):
        boards = []
        destinations = [take_root.upper_left, take_root.upper_right, take_root.lower_left, take_root.lower_right]
        last = not(any(destinations))

        if last:
            boards.append(board)
        for dest in destinations:
            if dest:
                for pot_dest in dest:
                    temp_board = deepcopy(board)
                    el, er = pot_dest.coords
                    rules.execute_take(el, er, temp_board, take_root)
                    boards.extend(self.find_boards_after_take(temp_board, pot_dest))
        return boards

    def evaluate_moves(self, board, active_player):
        scores = []
        moves_eval, takes_eval = self.potential_moves(board, active_player)
        for move in moves_eval:
            temp_board = deepcopy(board)
            (sl, sr), (el, er) = move
            rules.execute_move(sl, sr, el, er, temp_board, rules.piece_exists(sl, sr, temp_board), active_player)
            scores.append(self.score_position(temp_board))

        after_take_boards = []
        for take in takes_eval:
            boards = self.find_boards_after_take(board, take)
            after_take_boards.extend(boards)
        for brd in after_take_boards:
            scores.append(self.score_position(brd))
        return scores

    def minmax(self, board, active_player, depth):
        if depth == 0 or rules.game_over(board, active_player):
            return board

        if active_player == self.color:  # player trying to maximize score
            max_score = float("-inf")

        else:  # player trying to minimize score
            min_score = float("inf")
