from abc import ABCMeta, abstractmethod
import checkers_rules as rules


class AI(metaclass=ABCMeta):
    def __init__(self, ia_color, adv_color):
        self.color = ia_color
        self.adversary_color = adv_color

    @staticmethod
    def potential_actions(board, active_player):
        pot_moves = []
        pot_takes = rules.find_all_possible_captures(board, active_player)

        if not pot_takes:
            pot_moves = rules.find_all_possible_moves(board, active_player)

        return pot_moves, pot_takes

    @abstractmethod
    def play(self, board):
        pass


if __name__ == "__main__":

    print(AI.__dict__.keys())
