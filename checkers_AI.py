import checkers_rules as rules
from copy import deepcopy
from random import randint
import functools
import time


def slow_play(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        time.sleep(1)
        return func(*args, **kwargs)
    return wrapper


class AI:
    def __init__(self, ia_color, adv_color):
        self.color = ia_color
        self.adversary_color = adv_color

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
    def potential_actions(board, active_player):
        pot_moves = []
        pot_takes = rules.find_all_possible_captures(board, active_player)

        if not pot_takes:
            pot_moves = rules.find_all_possible_moves(board, active_player)

        return pot_moves, pot_takes


class RandomAI(AI):
    @slow_play
    def play(self, board):
        pot_moves, pot_takes = self.potential_actions(board, self.color)
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
    def __init__(self, ia_color, adv_color, depth=3):
        super().__init__(ia_color, adv_color)
        self.depth = depth

    def find_boards_after_moves(self, board, active_player):
        boards = []
        moves_eval, takes_eval = self.potential_actions(board, active_player)
        for move in moves_eval:
            temp_board = deepcopy(board)
            (sl, sr), (el, er) = move
            rules.execute_move(sl, sr, el, er, temp_board, rules.piece_exists(sl, sr, temp_board), active_player)
            boards.append(temp_board)
        return boards

    def find_boards_after_take(self, board, take_root, first=True):
        boards = []
        destinations = [take_root.upper_left, take_root.upper_right, take_root.lower_left, take_root.lower_right]
        last = not(any(destinations))

        if last:
            return [board]
        for dest in destinations:
            if dest:
                for pot_dest in dest:
                    temp_board = deepcopy(board)
                    el, er = pot_dest.coords
                    rules.execute_take(el, er, temp_board, take_root)
                    if first:
                        boards.append((self.find_boards_after_take(temp_board, pot_dest, False), (take_root.coords, pot_dest.coords)))
                    else:
                        boards.extend(self.find_boards_after_take(temp_board, pot_dest, False))
        return boards

    def evaluate_moves(self, board, active_player):
        moves_eval, takes_eval = self.potential_actions(board, active_player)
        after_move_boards = []
        if moves_eval:
            for move in moves_eval:
                temp_board = deepcopy(board)
                (sl, sr), (el, er) = move
                rules.execute_move(sl, sr, el, er, temp_board, rules.piece_exists(sl, sr, temp_board), active_player)
                after_move_boards.append(([temp_board], ((sl, sr), (el, er))))
            return after_move_boards
        after_take_boards = []
        for take in takes_eval:
            boards = self.find_boards_after_take(board, take)
            after_take_boards.extend(boards)
        return after_take_boards

    def minmax(self, board, active_player, depth, leading_move=None):
        game_over, _ = rules.game_over(board, active_player)
        if game_over:
            return -20 if active_player == self.color else 20, leading_move  # there are 20 pieces so max score is 20
        if depth == 0:
            return self.score_position(board), leading_move

        eval_boards = self.evaluate_moves(board, active_player)

        if active_player == self.color:  # player trying to maximize score
            max_score = float("-inf")
            for brd in eval_boards:
                first_move = leading_move
                (test_boards, move) = brd
                for test_board in test_boards:
                    if first_move is None:
                        first_move = move

                    score, temp_move = self.minmax(test_board, self.adversary_color, depth-1, first_move)
                    if score > max_score:
                        max_score = score
                        best_move = temp_move
            return max_score, best_move

        else:  # player trying to minimize score
            min_score = float("inf")
            for brd in eval_boards:
                first_move = leading_move
                (test_boards, move) = brd
                for test_board in test_boards:
                    if first_move is None:
                        first_move = move

                    score, temp_move = self.minmax(test_board, self.color, depth-1, first_move)
                    if score < min_score:
                        min_score = score
                        best_move = temp_move
            return min_score, best_move

    def minmax_ab(self, board, active_player, depth, leading_move=None, alpha=float("-inf"), beta=float("inf")):
        game_over, _ = rules.game_over(board, active_player)
        if game_over:
            return -20 if active_player == self.color else 20, leading_move  # there are 20 pieces so max score is 20
        if depth == 0:
            return self.score_position(board), leading_move

        eval_boards = self.evaluate_moves(board, active_player)

        if active_player == self.color:  # player trying to maximize score
            max_score = float("-inf")
            for brd in eval_boards:
                first_move = leading_move
                (test_boards, move) = brd
                for test_board in test_boards:
                    if first_move is None:
                        first_move = move

                    score, temp_move = self.minmax_ab(test_board, self.adversary_color, depth-1, first_move, alpha, beta)
                    if score > max_score:
                        max_score = score
                        best_move = temp_move
                    alpha = max(score, alpha)
                    if alpha >= beta:
                        break
                if alpha >= beta:
                    break
            return max_score, best_move

        else:  # player trying to minimize score
            min_score = float("inf")
            for brd in eval_boards:
                first_move = leading_move
                (test_boards, move) = brd
                for test_board in test_boards:
                    if first_move is None:
                        first_move = move

                    score, temp_move = self.minmax_ab(test_board, self.color, depth-1, first_move, alpha, beta)
                    if score < min_score:
                        min_score = score
                        best_move = temp_move
                    beta = min(score, beta)
                    if beta <= alpha:
                        break
                if beta <= alpha:
                    break
            return min_score, best_move

    def play(self, board):
        _, ((sl, sr), (el, er)) = self.minmax_ab(board, self.color, self.depth)
        return sl, sr, el, er


ai_types = {"random": RandomAI,
            "minmax": MinmaxAI}

if __name__ == "__main__":
    ai = AI("ia_color", "adv_color")
    print(ai.__dict__)

    print(AI.__dict__.keys())
    print(RandomAI.__dict__.keys())
    print(MinmaxAI.__dict__.keys())
